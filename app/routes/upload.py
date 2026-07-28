from flask import Blueprint

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/")
def health_check():
    return {"status": "ok"}
