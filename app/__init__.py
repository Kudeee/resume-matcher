from flask import Flask, jsonify
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["UPLOAD_DIR"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "file too large"}), 413

    from app.routes.upload import upload_bp

    app.register_blueprint(upload_bp)

    return app
