import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import app.services.service_utils as utils
from pathlib import Path

TAXONOMY_PATH = Path(__file__).parent / 'skill_taxonomy.json'
CATEGORY = ['technical', 'tools', 'soft_skills', 'domain']

with open(TAXONOMY_PATH) as f:
    _taxonomy = json.load(f)

_REVERSE_LOOKUP = {}
_MAX_LEN = 1

for _category, _entries in _taxonomy.items():
    for _entry in _entries:
        for _form in [_entry['canonical']] + _entry.get('aliases', []):
            _tokens = tuple(utils.normalize(_form))

            if _tokens:
                _REVERSE_LOOKUP[_tokens] = (_entry['canonical'], _category)
                _MAX_LEN = max(_MAX_LEN, len(_tokens))


def match_taxonomy(text):
    tokens = utils.normalize(text)
    hits = {}
    i, n = 0, len(tokens)

    while i < n:
        matched = False

        for length in range(min(_MAX_LEN, n - i), 0, -1):
            span = tuple(tokens[i:i + length])

            if span in _REVERSE_LOOKUP:
                canonical, category = _REVERSE_LOOKUP[span]
                hits[canonical] = category
                i += length
                matched = True
                break

        if not matched:
            i += 1
    return hits


def get_top_word(jd):
    splitted_jd = utils.jd_splitter(jd)

    vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words=utils.custom_stop_words(),
                                 token_pattern=r"(?u)\b\w+(?:[-/+#'][\w+]*)*(?!\w)", norm=None)
    vector = vectorizer.fit_transform(splitted_jd)

    flatten_vec = vector.toarray().sum(axis=0)
    idx = np.argsort(flatten_vec)
    feature_name = vectorizer.get_feature_names_out()
    top_word = feature_name[idx[-20:]]

    return top_word


def keyword_extract(jd):
    taxonomy_hits = match_taxonomy(jd)
    top_tfidf = [t.lower() for t in get_top_word(jd)]

    categorized = {cat: [] for cat in CATEGORY}
    emphasized = []
    for term, category in taxonomy_hits.items():
        categorized[category].append(term)
        term_lower = term.lower()
        if any(term_lower in kw or kw in term_lower for kw in top_tfidf):
            emphasized.append(term)

    for cat in categorized:
        categorized[cat].sort()

    return {**categorized, 'emphasized': sorted(emphasized)}
