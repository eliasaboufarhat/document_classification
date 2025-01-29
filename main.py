import os
from dotenv import load_dotenv

from storage.db_utils import DBUtils
from pdf_parsing.queue_files import QueueFiles
from classification.classify import Classifier


class Main:

    def __init__(self):
        load_dotenv(override=True)

        self.db = DBUtils(
            db_name="ashvin",
            user=os.environ.get("MONGO_USER"),
            password=os.environ.get("MONGO_PASSWORD"),
        )

        self.db.connect()
        pass

    def query_by_clusters(self):

        data = self.db.query()

        clusters = {data[i]["cluster_id"]: [] for i in range(len(data))}
        for item in clusters:
            for doc in data:
                if doc["cluster_id"] == item:
                    clusters[item].append(doc)
        return clusters

    def delete_session(self):
        data = self.db.query()
        document_ids = {data[i]["document_id"]: [] for i in range(len(data))}

        for doc in document_ids:
            self.db.delete({"document_id": doc})

        return

    def rerun(self):

        files_extractor = QueueFiles(data_dir="./data")
        files_extractor.run()

        classifier = Classifier(privacy=True)
        classifier.pre_process_docs(docs=files_extractor.docs)
        classifier.run()

        for doc in classifier.docs:
            self.db.insert(doc)


if __name__ == "__main__":
    load_dotenv(override=True)
    # main_class = Main()
    # main()
