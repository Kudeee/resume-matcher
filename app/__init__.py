from urllib import response

from flask import Flask, jsonify
from flask_cors import CORS
from app.exceptions import AppError


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    @app.errorhandler(AppError)
    def handle_app_error(err):
        response = jsonify(err.to_dict())
        response.status_code = err.status_code
        return response

    from app.routes.upload import upload_bp
    from app.routes.analyze import analyze_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(pages_bp)

    return app
