from flask import Blueprint, jsonify, request
import os
import io
import uuid
from app.services import parser

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload_resume():
    file = request.files.get("file")

    ALLOWED_EXT = {".pdf", ".docx"}

    if file is None or not file.filename:
        return jsonify({"error": "no file added"}), 400

    root, ext = os.path.splitext(file.filename)

    if ext.lower() not in ALLOWED_EXT:
        return jsonify({"error": "file not accepted"}), 400

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
            {"resume_id": str(file_id), "sections": sections, "raw_text": extracted_file, "formatting": formatting})

    except Exception as e:
        print(e)
        return jsonify({"error": "failed to process file"}), 500
