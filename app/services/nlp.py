import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
            _tokens = tuple(utils._normalize(_form))

            if _tokens:
                _REVERSE_LOOKUP[_tokens] = (_entry['canonical'], _category)
                _MAX_LEN = max(_MAX_LEN, len(_tokens))


def keyword_extract(jd):
    taxonomy_hits = utils.match_taxonomy(jd, _REVERSE_LOOKUP, _MAX_LEN)
    top_tfidf = [t.lower() for t in utils.get_top_word(jd)]

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


def test():
    jd = '''We are looking for a Senior Backend Engineer to join our growing platform team.

Responsibilities:
- Design and build scalable REST APIs using Python and Flask
- Collaborate closely with the team and cross-functional stakeholders
- Own the full lifecycle of backend services from design to deployment
- Deploy and monitor services using Docker and Kubernetes on AWS
- Write and maintain CI/CD pipelines using Jenkins and GitHub Actions
- Support the team during on-call rotations and incident response
- Lead the team through agile sprint planning and backlog grooming
- Optimize PostgreSQL queries and database schema design
- Mentor junior engineers and support the team's technical growth
- Communicate effectively with product managers and other teams

Requirements:
- 5+ years of experience building backend systems in Python
- Strong experience with relational databases such as PostgreSQL or MySQL
- Hands-on experience with Docker, Kubernetes, and infrastructure as code (Terraform)
- Solid understanding of RESTful API design and microservices architecture
- Experience with CI/CD tooling and automated testing practices
- Excellent communication and collaboration skills
- Strong problem-solving ability and sense of ownership
- Familiarity with monitoring tools such as Datadog or Prometheus
- Experience working in an Agile/Scrum environment
- Bachelor's degree in Computer Science or equivalent practical experience'''

    return keyword_extract(jd)
