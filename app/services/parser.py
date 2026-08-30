import pdfplumber
from docx.table import Table
from docx.text.paragraph import Paragraph
from . import service_utils as utils
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
    full_doc = []
    formatting = {'issues': [], 'passed': True}

    for idx, block in enumerate(document.iter_inner_content(), start=1):
        current_block = {'block': idx, 'issue': []}
        if isinstance(block, Paragraph):
            full_doc.append(block.text)
            if utils.paragraph_contains_image(block):
                current_block['issue'].append('image')

        elif isinstance(block, Table):
            current_block['issue'].append('table')
            for row in block.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        full_doc.append(para.text)
                        if utils.paragraph_contains_image(para):
                            current_block['issue'].append('image inside the table')
        if current_block['issue']:
            formatting['issues'].append(current_block)

    if formatting['issues']:
        formatting['passed'] = False

    return full_doc, formatting


def extract_text_from_pdf(file_path):
    try:
        full_doc = []
        formatting = {'issues': [], 'passed': True}
        with pdfplumber.open(file_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                boundary = utils.find_column_boundary(page)
                current_page = {'page': idx, 'issue': []}

                if page.images:
                    current_page['issue'].append('image')
                if page.find_table():
                    current_page['issue'].append('table')

                if boundary:
                    left = page.within_bbox((0, 0, boundary, page.height))
                    right = page.within_bbox((boundary, 0, page.width, page.height))
                    l_text = left.extract_text() or ""
                    r_text = right.extract_text() or ""
                    full_text = l_text + "\n" + r_text
                    doc = [
                        para.strip() for para in full_text.split("\n") if para.strip()
                    ]
                    full_doc.extend(doc)
                else:
                    text = page.extract_text() or ""
                    doc = [
                        para.strip() for para in text.split("\n") if para.strip()
                    ]
                    full_doc.extend(doc)

                if current_page['issue']:
                    formatting['issues'].append(current_page)

        if formatting['issues']:
            formatting['passed'] = False

        return full_doc, formatting

    except ValueError:
        return "File is corrupted"


def test():
    t, f = extract_text_from_docx('test_resume/resume_docx_image_table.docx')
    # t, f = extract_text_from_pdf('test_resume/resume_image_table.pdf')

    print(f)

    return 'a'
