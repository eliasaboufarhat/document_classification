from pdf_parsing.queue_files import QueueFiles
from classification.classify import Classifier


def main():
    files_extractor = QueueFiles(data_dir="data")
    files_extractor.run()

    classifier = Classifier()
    classifier.pre_process_docs(docs=files_extractor.docs)
    labels = classifier.run()

    print(labels)


if __name__ == "__main__":
    main()
