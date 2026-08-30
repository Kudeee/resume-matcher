from flask import Flask, jsonify
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"error": "file too large"}), 413

    from app.routes.upload import upload_bp
    from app.routes.analyze import analyze_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(analyze_bp)

    return app
