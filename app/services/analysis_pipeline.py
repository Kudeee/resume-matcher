import app.services.nlp as nlp
import app.services.scorer as scorer


def analyze_pipeline(resume_text, jd_text):
    jd_matched = nlp.match_taxonomy(jd_text)
    resume_matched = nlp.match_taxonomy(resume_text)

    per_cat_score = scorer.per_category_score(resume_matched, jd_matched)
    overall_score = scorer.overall_score(per_cat_score)
    overall_similarity = scorer.overall_similarity(resume_text, jd_text)
    kw = scorer.matched_missing_keywords(resume_matched, jd_matched)

    analysis_output = {'overall_score': overall_score, 'category_scores': per_cat_score,
                       'overall_sim': overall_similarity,
                       'missing_keywords': kw['missing_kw'], 'matched_keywords': kw['matched_kw']}

    return analysis_output
