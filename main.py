import os
from dotenv import load_dotenv

from storage.db_utils import DB
from pdf_parsing.queue_files import QueueFiles
from classification.classify import Classifier


def main():
    load_dotenv(override=True)

    database = DB(
        db_name="ashvin",
        user=os.environ.get("MONGO_USER"),
        password=os.environ.get("MONGO_PASSWORD"),
    )

    database.connect()

    files_extractor = QueueFiles(data_dir="./data")
    files_extractor.run()

    classifier = Classifier(privacy=True)
    classifier.pre_process_docs(docs=files_extractor.docs)
    classifier.run()

    for doc in classifier.docs:
        database.insert(doc)


if __name__ == "__main__":
    main()
