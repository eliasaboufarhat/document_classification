import os
from openai import OpenAI
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

# ------|| Idea ||------
# 1. Document Level Classification
# 2. Multiple Chunks Classification and take majority vote


class Classifier:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.n_clusters = 6
        self.docs = []
        self.processed_docs = []

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
        # distinct_labels = set(cluster_labels)

        # for cluster_idx in distinct_labels:
        #     indices_in_cluster = np.where(cluster_labels == cluster_idx)[0]
        #     centroid = kmeans.cluster_centers_[cluster_idx]

        #     distances = []
        #     for idx in indices_in_cluster:
        #         dist = np.linalg.norm(embeddings[idx] - centroid)
        #         distances.append((idx, dist))

        #     distances.sort(key=lambda x: x[1])
        #     top_docs = distances[:3]

        # representative_texts = [docs[idx] for (idx, d) in top_docs]

        return cluster_labels

    def embed(self, docs):
        embeddings = self.model.encode(docs)
        return embeddings

    def predict_labels(self, cluster_id, text_snippet, candidate_labels):
        prompt = f"""
        I have the following documents metadata and text in one cluster:
        {text_snippet}

        Based on the content, choose the most appropriate label from this list or suggest a new one if it does not exists:
        {candidate_labels}

        Return the result as JSON format. Make sure to follow this structure 
        {{
            "label": "In here will be your label",
        }}
        """

        if not self.client:
            return f"Cluster {cluster_id}"

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a classifier assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        try:
            answer = response["choices"][0]["message"]["content"]

            if "label" in answer:
                return answer["label"]
        except Exception as e:
            print(f"Error in predicting labels: {e}")
            return f"Cluster {cluster_id}"


# if __name__ == "__main__":
#     docs = [
#         "Machine learning algorithms have revolutionized the field of AI.",
#         "Deep learning and neural networks are subsets of machine learning.",
#         "Artificial intelligence applications range from healthcare to finance.",
#         "AI and automation are reshaping industries across the globe.",
#         "Climate change and global warming are pressing issues for humanity.",
#         "The impact of renewable energy on the global economy is profound.",
#         "Space exploration has led to significant advancements in science.",
#         "NASA’s Mars rover has been a breakthrough in space research.",
#         "The discovery of new exoplanets excites the field of astronomy.",
#         "Quantum computing has the potential to revolutionize cryptography.",
#         "Blockchain technology is widely used in cryptocurrency applications.",
#         "Bitcoin and Ethereum are two of the most popular cryptocurrencies.",
#         "The benefits of regular exercise include improved mental health.",
#         "A balanced diet and good nutrition are key to staying healthy.",
#         "Meditation and mindfulness can reduce stress and improve focus.",
#         "The history of art is a reflection of cultural evolution over time.",
#         "Modern architecture combines function and aesthetics beautifully.",
#         "The smartphone industry is constantly evolving with new innovations.",
#         "Social media platforms have transformed how people communicate.",
#         "The rise of e-commerce has changed consumer shopping habits.",
#     ]
#     classifier = Classifier()
#     classifier.run(docs)
