import os
import json
from openai import OpenAI
import numpy as np
from pydantic import BaseModel
from joblib import dump, load
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

from classification.llm import LLM

# ------|| Idea ||------
# 1. Document Level Classification
# 2. Multiple Chunks Classification and take majority vote


class Label(BaseModel):
    label: str


class Classifier:
    def __init__(self, privacy=True):
        self.model = SentenceTransformer("msmarco-bert-base-dot-v5")
        self.model_clustering_path = "model/kmeans.pkl"
        self.n_clusters = 6
        self.labels = []
        self.llm = LLM()
        self.privacy = privacy
        self.mapping_labels = {}

        try:
            self.client = OpenAI(api_key=os.environ.get("OPEN_AI_SECRET_KEY", None))
        except Exception as e:
            self.client = None

    def pre_process_docs(self, docs):

        processed_docs = []
        for doc in docs:
            full_text = ""
            for page in doc["pages"]:
                full_text_per_page = (
                    page["raw_text"]
                    + " ".join([img["ocr_text"] for img in page["images_with_text"]])
                    + " ".join([str(tbl["data"]) for tbl in page["tables"]])
                )
                full_text += full_text_per_page + "\n"

            processed_docs.append(full_text)
        return processed_docs

    def run(self, docs, preprocessed_docs):
        """
        Use an incremental  k-means approach
        MiniBatchKMens: Update centroids incrementally with new samples
        """

        if not preprocessed_docs or preprocessed_docs == []:
            return

        embeddings = self.embed(preprocessed_docs)

        kmeans = KMeans(n_clusters=6, random_state=42)
        kmeans.fit(embeddings)

        cluster_labels = kmeans.labels_
        distinct_labels = set(cluster_labels)
        self.mapping_labels = {}

        for cluster_idx in distinct_labels:
            indices_in_cluster = np.where(cluster_labels == cluster_idx)[0]
            centroid = kmeans.cluster_centers_[cluster_idx]

            distances = []
            for idx in indices_in_cluster:
                dist = np.linalg.norm(embeddings[idx] - centroid)
                distances.append((idx, dist))

            distances.sort(key=lambda x: x[1])
            top_docs = distances
            representative_docs = [docs[idx] for (idx, d) in top_docs]
            self.mapping_labels[cluster_idx] = self.predict_labels(
                cluster_idx, representative_docs
            )

        for doc_id in range(len(cluster_labels)):
            docs[doc_id]["label"] = self.mapping_labels[cluster_labels[doc_id]]
            docs[doc_id]["cluster_id"] = int(cluster_labels[doc_id])

        kmeans.mapping_labels = self.mapping_labels

        if os.path.exists(self.model_clustering_path):
            os.remove(self.model_clustering_path)

        dump(kmeans, self.model_clustering_path)

        return docs

    def predict(self, doc, processed_doc):
        if os.path.exists(self.model_clustering_path):
            kmeans = load(self.model_clustering_path)
            cluster = kmeans.predict(self.embed(processed_doc))
            doc["cluster_id"] = int(cluster[0])
            doc["label"] = kmeans.mapping_labels[cluster[0]]
            return doc
        else:
            doc["cluster_id"] = -1
            doc["label"] = "Unknown"
            return doc

    def embed(self, docs):
        embeddings = self.model.encode(docs)
        return embeddings

    def predict_labels(self, cluster_id, text_snippet):
        prompt = f"""
You are an expert in document classification. Your task is to assign a **concise and general category label** to a given cluster of documents based on their **metadata and text content**. 

### Instructions:
- The **cluster label** should capture the main theme or topic that best describes the documents.
- The label **must be short and general**, like the following examples: `"prescription"`, `"order"`, `"health"`, `"recipe"`, etc.
- **Do NOT** generate a sentence or a paragraph. The label should be **a single category name**.
- Ensure the label is **accurate**, **representative**, and **concise**.

### Cluster Data:
Metadata and Text: {str(text_snippet)}

### Output Format:
Return your response as a **valid JSON** object in the following format:
```json
{{
    "label": "The cluster label here"
}}
"""
        if self.privacy == True:
            try:
                label = self.llm.run(prompt, Label)
                # self.labels.append(label.label)
                return label.label
            except Exception as e:
                print(f"Error in predicting labels: {e}")
                return f"Cluster {cluster_id}"

        if not self.client:
            return f"Cluster {cluster_id}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a classifier assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            label = json.loads(response.choices[0].message.content)
            return label["label"]
        except Exception as e:
            print(f"Error in predicting labels: {e}")
            return f"Cluster {cluster_id}"
