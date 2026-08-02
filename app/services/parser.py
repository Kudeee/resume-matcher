import pdfplumber
from . import extract_utils as eu
from docx import Document


def section_detector(text):
    SECTION_ALIASES = {
        "summary": ["summary", "objective", "profile"],
        "experience": [
            "experience",
            "work history",
            "professional experience",
            "employment",
        ],
        "skills": ["skills", "technical skills", "core competencies"],
        "education": ["education", "academic background"],
        "projects": ["projects", "personal projects"],
    }

    alias_to_canonical = {
        variant: canonical
        for canonical, variants in SECTION_ALIASES.items()
        for variant in variants
    }

    buckets = {"head": [], **{canon: [] for canon in SECTION_ALIASES}}
    current_section = "head"

    for section in text:
        s = section.rstrip(":-–— ").lower()
        if s in alias_to_canonical:
            current_section = alias_to_canonical[s]
            continue
        else:
            if s:
                buckets[current_section].append(section)
            else:
                continue

    sections = {**{key: "\n".join(val) for key, val in buckets.items()}}

    return sections


def extract_text_from_docx(file_path):
    document = Document(file_path)
    extracted_table_text = eu.table_document(document)

    if extracted_table_text:
        return extracted_table_text
    else:
        return [paragraph.text for paragraph in document.paragraphs]


def extract_text_from_pdf(file_path):
    try:
        full_doc = []
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
