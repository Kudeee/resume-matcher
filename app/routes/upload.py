from flask import Blueprint, current_app, jsonify, request
import os
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

    if ext not in ALLOWED_EXT:
        return jsonify({"error": "file not acceted"}), 400

    file_id = uuid.uuid4()

    file_path = os.path.join(current_app.config["UPLOAD_DIR"], f"{file_id}{ext}")
    file.save(file_path)

    try:
        extracted_file = []
        if ext == ".pdf":
            extracted_file = parser.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            extracted_file = parser.extract_text_from_docx(file_path)

        sections = parser.section_detector(extracted_file)

        return jsonify({"sections": sections, "raw_text": extracted_file})

    except Exception as e:
        print(e)
        return jsonify({"error": "failed to process file"}), 500
