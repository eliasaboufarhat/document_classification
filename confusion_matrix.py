import os
import numpy as np
import pandas as pd
from joblib import load

import seaborn as sns
from dotenv import load_dotenv

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from storage.db_utils import DBUtils

if __name__ == "__main__":

    cluster_mapping = {
        0: "Physician",
        1: "Order",
        2: "Compliance",
        3: "Delivery",
        4: "Prescription",
        5: "Sleep",
    }

    data_dir = "./data"
    load_dotenv(override=True)

    db = DBUtils(
        db_name="ashvin",
        user=os.environ.get("MONGO_USER"),
        password=os.environ.get("MONGO_PASSWORD"),
    )
    db.connect()

    mapping_true_labels = {}
    true_labels_list = []

    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            f = os.path.join(data_dir, filename)
            if os.path.isfile(f) and f.lower().endswith(".pdf"):
                base_name = os.path.basename(f)
                true_label = base_name.split(" ")[0]
                mapping_true_labels[f] = true_label
                true_labels_list.append(true_label)

    mapping_predicted_labels = {}
    data = db.query()

    for doc in data:
        mapping_predicted_labels[doc["document_id"]] = cluster_mapping[
            doc["cluster_id"]
        ]
    unique_true_labels = sorted(set(true_labels_list))
    unique_predicted_labels = sorted(cluster_mapping.values())

    true_labels = [mapping_true_labels[f] for f in mapping_true_labels]
    predicted_labels = [mapping_predicted_labels[f] for f in mapping_true_labels]

    cm = confusion_matrix(true_labels, predicted_labels, labels=unique_true_labels)

    df_cm = pd.DataFrame(
        cm,
        index=[f"Actual - {c}" for c in unique_true_labels],
        columns=[f"Prediction - {c}" for c in unique_predicted_labels],
    )

    plt.figure(figsize=(8, 6))
    sns.heatmap(df_cm, annot=True, fmt="d", cmap="Blues", linewidths=0.5)
    plt.xlabel("Predicted Category")
    plt.ylabel("True Category")
    plt.title("Confusion Matrix for 6-Cluster Classification")
    plt.show()

    accuracy = np.trace(cm) / np.sum(cm)
    print(f"Classification Accuracy: {accuracy:.2f}")

    reportt = classification_report(
        true_labels, predicted_labels, labels=unique_true_labels
    )
    print("Classification Report:\n", reportt)
