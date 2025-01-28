import pdfplumber
import pytesseract
from PIL import Image


class WorkerPDFParser:

    def __init__(self):
        pass

    def run(self, file_path):
        results = {"document_id": file_path, "pages": []}

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Text & tables
                text, table_data = self.parse_page_text_and_tables(page)
                # Images
                try:
                    images_ocr = self.parse_images_with_ocr(page)
                except ValueError:
                    images_ocr = []
                    print(f"Error in images OCR for {file_path} - pags {i + 1}")

                page_info = {
                    "page_number": i + 1,
                    "raw_text": text,
                    "tables": table_data,
                    "images_with_text": images_ocr,
                }
                results["pages"].append(page_info)

        return results

    def parse_page_text_and_tables(self, page):
        text = page.extract_text() or ""
        table_data = []
        tables = page.extract_tables() or []

        for idx, tbl in enumerate(tables):
            if not tbl:
                continue

            cleaned_table = []
            for row in tbl:
                cleaned_row = [(cell if cell is not None else "") for cell in row]
                if any(cleaned_row):
                    cleaned_table.append(cleaned_row)
            if cleaned_table:
                table_data.append({"table_number": idx + 1, "data": cleaned_table})
        return text, table_data

    def parse_images_with_ocr(self, page):
        """
        TODO: There is an error in this method
        """
        images_with_text = []

        for img_idx, img in enumerate(page.images):
            x0 = img["x0"]
            top = img["top"]
            x1 = img["x1"]
            bottom = img["bottom"]
            cropped_page = page.crop((x0, top, x1, bottom))
            page_image = cropped_page.to_image(resolution=300).original
            ocr_text = pytesseract.image_to_string(page_image)
            images_with_text.append(
                {
                    "image_id": img_idx + 1,
                    "box": [x0, top, x1, bottom],
                    "ocr_text": ocr_text,
                }
            )
        return images_with_text
