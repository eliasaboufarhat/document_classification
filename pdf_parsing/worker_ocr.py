import pdfplumber
import pytesseract


class WorkerOCR:

    def __init__(self):
        pass

    def run(self, file_path):
        results = {"document_id": file_path, "pages": []}
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                pil_image = page.to_image(resolution=300).original
                extracted_text = pytesseract.image_to_string(pil_image)
                results["pages"].append(
                    {
                        "page_number": i + 1,
                        "raw_text": extracted_text,
                        "tables": [],
                        "images_with_text": [],
                    }
                )

        return results
