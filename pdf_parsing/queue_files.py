import os
import json
import pdfplumber

from pdf_parsing.worker_ocr import WorkerOCR
from pdf_parsing.worker_pcr_parser import WorkerPDFParser
from constants import MIN_TEXT_LENGTH


class QueueFiles:
    def __init__(self, data_dir="./data_test"):
        self.data_dir = data_dir

        self.ocr = WorkerOCR()
        self.pdf_parser = WorkerPDFParser()

    def run(self):
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                f = os.path.join(self.data_dir, filename)
                if os.path.isfile(f) and f.split(".")[-1] == "pdf":
                    result = self.check_extraction_technique(f)

                    print(f"{filename} - {result}")
                    if result == "ocr":
                        content = self.ocr.run(f)

        return

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
