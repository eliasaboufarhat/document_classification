import pdfplumber
import pytesseract
from PIL import Image


class WorkerOCR:

    def __init__(self):
        pass

    def run(self, file_path):
        text_pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                pil_image = page.to_image(resolution=300).original
                extracted_text = pytesseract.image_to_string(pil_image)
                text_pages.append({"page_number": i + 1, "content": extracted_text})

        return text_pages
