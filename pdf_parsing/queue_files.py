import os
import json
import pdfplumber
import shutil

from pdf_parsing.worker_ocr import WorkerOCR
from pdf_parsing.worker_pdf_parser import WorkerPDFParser
from constants import MIN_TEXT_LENGTH


class QueueFiles:
    def __init__(self, data_dir="./data_test"):
        self.data_dir = data_dir

        self.ocr = WorkerOCR()
        self.pdf_parser = WorkerPDFParser()

    def run(self):
        docs = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                f = os.path.join(self.data_dir, filename)
                if os.path.isfile(f) and f.lower().endswith(".pdf"):
                    content = self.process_pdf(f)
                    docs.append(content)
        return docs

    def run_one_pdf(self, file_path):
        if os.path.isfile(file_path) and file_path.lower().endswith(".pdf"):
            doc = self.process_pdf(file_path)
            shutil.move(
                file_path, os.path.join(self.data_dir, os.path.basename(file_path))
            )
            return doc
        else:
            print(f"Invalid file: {file_path}")
            return None

    def process_pdf(self, file_path):
        result = self.check_extraction_technique(file_path)
        print(f"{os.path.basename(file_path)} - {result}")

        if result == "ocr":
            content = self.ocr.run(file_path)
            content["method"] = "ocr"
        elif result == "text":
            content = self.pdf_parser.run(file_path)
            content["method"] = "text"
        else:
            print(f"Unknown extraction method for {file_path}")
            return None

        return content

    def check_extraction_technique(self, file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                total_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        total_text += page_text
                if len(total_text) < MIN_TEXT_LENGTH:
                    return "ocr"
                return "text"
        except Exception as e:
            print(f"Error when Opening File {file_path} - {type(e)}")
        return


if __name__ == "__main__":

    files_extractor = QueueFiles()
    files_extractor.run()
