from flask import Blueprint, jsonify, request
import os
import io
import uuid
from app.services import parser
from app.exceptions import AppError, NoFileProvidedError, UnsupportedFileTypeError, ParsingError

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload_resume():
    file = request.files.get("resume")

    ALLOWED_EXT = {".pdf", ".docx"}

    if file is None or not file.filename:
        raise NoFileProvidedError()

    root, ext = os.path.splitext(file.filename)

    if ext.lower() not in ALLOWED_EXT:
        raise UnsupportedFileTypeError(f"'{ext}' is not a supported file type. Please upload a PDF or DOCX.")

    file_id = uuid.uuid4()

    file_temp = io.BytesIO(file.read())

    try:
        extracted_file = []
        formatting = {}
        if ext.lower() == ".pdf":
            extracted_file, formatting = parser.extract_text_from_pdf(file_temp)
        elif ext.lower() == ".docx":
            extracted_file, formatting = parser.extract_text_from_docx(file_temp)

        sections = parser.section_detector(extracted_file)

        return jsonify(
            {"resume_id": str(file_id), "sections": sections, "resume_text": extracted_file, "formatting": formatting})

    except AppError:
        raise
    except Exception as e:
        print(e)
        raise ParsingError()
