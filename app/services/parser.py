import pdfplumber
from . import extract_utils as eu


def extract_text_from_pdf(file_path):
    try:
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                boundary = eu.find_column_boundary(page)
                if boundary:
                    left = page.within_bbox((0, 0, boundary, page.height))
                    right = page.within_bbox((boundary, 0, page.width, page.height))
                    text.append(
                        (left.extract_text() or "")
                        + "\n"
                        + (right.extract_text() or "")
                    )
                else:
                    text.append(page.extract_text() or "")

        return "\n".join(text)

    except FileNotFoundError:
        return "File not found."

    except ValueError:
        return "File is corrupted"
