import os
import json
from openai import OpenAI
import numpy as np
from pydantic import BaseModel
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
        self.n_clusters = 6
        self.docs = []
        self.processed_docs = []
        self.labels = []
        self.llm = LLM()
        self.privacy = privacy
        self.mapping_labels = {}

        try:
            self.client = OpenAI(api_key=os.environ.get("OPEN_AI_SECRET_KEY", None))
        except Exception as e:
            self.client = None

    def pre_process_docs(self, docs):
        self.docs = docs
        self.processed_docs = []
        for doc in docs:
            full_text = ""
            for page in doc["pages"]:
                full_text_per_page = (
                    page["raw_text"]
                    + " ".join([img["ocr_text"] for img in page["images_with_text"]])
                    + " ".join([tbl["data"] for tbl in page["tables"]])
                )
                full_text += full_text_per_page + "\n"

            self.processed_docs.append(full_text)
        return

    def run(self):
        """
        Use an incremental  k-means approach
        MiniBatchKMens: Update centroids incrementally with new samples
        """

        if not self.processed_docs or self.processed_docs == []:
            return

        embeddings = self.embed(self.processed_docs)

        kmeans = KMeans(n_clusters=6, random_state=42)
        kmeans.fit(embeddings)
        cluster_labels = kmeans.labels_
        distinct_labels = set(cluster_labels)

        for cluster_idx in distinct_labels:
            indices_in_cluster = np.where(cluster_labels == cluster_idx)[0]
            centroid = kmeans.cluster_centers_[cluster_idx]

            distances = []
            for idx in indices_in_cluster:
                dist = np.linalg.norm(embeddings[idx] - centroid)
                distances.append((idx, dist))

            distances.sort(key=lambda x: x[1])
            # top_docs = distances[:3]
            top_docs = distances
            representative_docs = [self.docs[idx] for (idx, d) in top_docs]
            self.mapping_labels[cluster_idx] = self.predict_labels(
                cluster_idx, representative_docs
            )

        for doc_id in range(len(cluster_labels)):
            self.docs[doc_id]["label"] = self.mapping_labels[cluster_labels[doc_id]]
            self.docs[doc_id]["cluster_id"] = cluster_labels[doc_id]

        return self.docs

    def embed(self, docs):
        embeddings = self.model.encode(docs)
        return embeddings

    def predict_labels(self, cluster_id, text_snippet):
        prompt = f"""
I have a cluster of documents, each containing metadata and text. A "cluster label" is the most representative category for the group of documents in the cluster, capturing the main theme or topic that best describes their content and metadata. Should be a simple general category name like 'Prescription', 'Order', 'Recipe'.

Here is the cluster you need to label:
Metadata and Text: {str(text_snippet)}

Return your answer in the following JSON format. Make sure the label is concise and accurately represents the content of the cluster:
{{
    "label": "The cluster label here",
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
