import pdfplumber
from . import extract_utils as eu
from docx import Document


def extract_text_from_docx(file_path):
    document = Document(file_path)
    mul_col = eu.table_document(document)

    if mul_col:
        return mul_col
    else:
        full_doc = [paragraph.text for paragraph in document.paragraphs]
        print(full_doc)

        return "\n".join(full_doc)


def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                boundary = eu.find_column_boundary(page)
                if boundary:
                    left = page.within_bbox((0, 0, boundary, page.height))
                    right = page.within_bbox((boundary, 0, page.width, page.height))
                    l_text = left.extract_text() or ""
                    r_text = right.extract_text() or ""
                    full_text = l_text + "\n" + r_text
                    full_doc = [
                        para.strip() for para in full_text.split("\n") if para.strip()
                    ]
                    return full_doc
                else:
                    text = page.extract_text() or ""
                    full_doc = [
                        para.strip() for para in text.split("\n") if para.strip()
                    ]
                    return full_doc

    except FileNotFoundError:
        return "File not found."

    except ValueError:
        return "File is corrupted"
