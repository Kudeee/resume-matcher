from flask import Blueprint, jsonify, request
from app.services.analysis_pipeline import analyze_pipeline as anpip
from app.exceptions import AppError, InvalidRequestError, MissingFieldError, AnalysisError

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)

    if data is None:
        raise InvalidRequestError("Request body must be JSON.")

    raw_text = data.get('resume_text')
    jd_text = data.get('jd_text')
    formatting = data.get('formatting')

    if isinstance(raw_text, list):
        raw_text = " ".join(raw_text)

    if not raw_text:
        raise MissingFieldError('resume_text')
    if not jd_text:
        raise MissingFieldError('jd_text')

    try:
        analyze_output = anpip(raw_text, jd_text)
    except AppError:
        raise
    except Exception as e:
        print(e)
        raise AnalysisError()

    analyze_output["formatting"] = formatting

    return jsonify(analyze_output)
