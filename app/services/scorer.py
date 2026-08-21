from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import app.services.service_utils as utils
from app.services.nlp import CATEGORY

CATEGORY_WEIGHTS = {'technical': 0.50, 'tools': 0.25, 'soft_skills': 0.15, 'domain': 0.10}


def per_category_score(resume_hits, jd_hits):
    category_scores = {}

    for category in CATEGORY:
        jd_terms = {term for term, cat in jd_hits.items() if cat == category}
        resume_terms = {term for term, cat in resume_hits.items() if cat == category}

        matched = jd_terms & resume_terms
        category_scores[category] = round(100 * len(matched) / len(jd_terms)) if jd_terms else None
    return category_scores


def matched_missing_keywords(resume_hits, jd_hits):
    missing_matched = {'missing_kw': [], 'matched_kw': []}

    jd_terms = {term for term, cat in jd_hits.items()}
    resume_terms = {term for term, cat in resume_hits.items()}

    missing_matched['missing_kw'].extend(sorted(jd_terms - resume_terms))
    missing_matched['matched_kw'].extend(sorted(jd_terms & resume_terms))

    return missing_matched


def overall_similarity(resume, jd):
    vectorizer = TfidfVectorizer(stop_words=utils.custom_stop_words(),
                                 token_pattern=r"(?u)\b\w+(?:[-/+#'|.—][\w+]+)*\b")
    vector = vectorizer.fit_transform([resume, jd])
    return cosine_similarity(vector[0], vector[1])[0][0]


def overall_score(scores):
    weighted_sum = 0
    weight_total = 0
    for category, weight in CATEGORY_WEIGHTS.items():
        score = scores[category]
        if score is not None:
            weighted_sum += score * weight
            weight_total += weight

    return round(weighted_sum / weight_total) if weight_total else None
