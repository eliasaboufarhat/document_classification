import os
import json
import time
from dotenv import load_dotenv

from storage.db_utils import DBUtils
from pdf_parsing.queue_files import QueueFiles
from classification.classify import Classifier


class Queue:

    def __init__(self):
        load_dotenv(override=True)
        self.db = DBUtils(
            db_name="ashvin",
            user=os.environ.get("MONGO_USER"),
            password=os.environ.get("MONGO_PASSWORD"),
        )
        self.db.connect()

    def run(self):
        while True:
            status = self.process_queue()
            if not status:
                break
            time.sleep(5)
        return

    def process_file(self, file_path):
        files_extractor = QueueFiles(data_dir="./data")

        doc = files_extractor.run_one_pdf(file_path)

        classifier = Classifier(privacy=True)
        pre_processed_docs = classifier.pre_process_docs(docs=[doc])
        doc = classifier.predict(doc, pre_processed_docs)
        self.db.insert(doc)

    def process_queue(self):
        try:
            with open("queue.json", "r") as f:
                queue = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Queue file not found or empty.")
            return False

        if not queue:
            print("No pending files in the queue.")
            return True

        task = queue.pop(0)

        print(f"Processing file: {task['file']}")

        task["status"] = "processing"
        with open("queue.json", "w") as f:
            json.dump(queue, f, indent=4)
        self.process_file(task["file"])
        with open("queue.json", "w") as f:
            json.dump(queue, f, indent=4)
        return True


if __name__ == "__main__":
    queue = Queue()
    queue.run()
