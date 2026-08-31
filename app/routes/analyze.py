from flask import Blueprint, jsonify, request
from app.services.analysis_pipeline import analyze_pipeline as anpip

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "request did not get anything"}), 400

    raw_text = data.get('resume_text')
    jd_text = data.get('jd_text')
    formatting = data.get('formatting')

    if isinstance(raw_text, list):
        raw_text = " ".join(raw_text)

    if not raw_text or not jd_text:
        return jsonify({'error': 'resume raw_text and jd_text is required'}), 400

    try:
        analyze_output = anpip(raw_text, jd_text)

        analyze_output["formatting"] = formatting

        return jsonify(analyze_output)
    except Exception as e:
        print(e)
        return jsonify({"error": "something's wrong"}), 500
