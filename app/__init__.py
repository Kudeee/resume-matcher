from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    from app.routes.upload import upload_bp

    app.register_blueprint(upload_bp)

    return app
