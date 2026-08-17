import numpy as np
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


def normalize(text):
    text = text.lower().replace('-', ' ').replace('/', ' ').replace('—', ' ')
    text = re.sub(r"[^\w\s+#]", ' ', text)

    return text.split()


def custom_stop_words():
    custom_words = ENGLISH_STOP_WORDS.union(
        ['responsibilities', 'requirements', 'qualifications', 'duties', 'description',
         'overview', 'summary', 'role', 'position', 'title', 'apply', 'application',
         'applicant', 'candidate', 'candidates', 'resume', 'cv', 'submit', 'please',
         'contact', 'strong', 'excellent', 'proven', 'demonstrated', 'ability',
         'abilities', 'good', 'great', 'highly', 'effective', 'efficient', 'various',
         'wide', 'range', 'company', 'organization', 'team', 'environment', 'culture',
         'mission', 'opportunity', 'opportunities', 'join', 'growing', 'dynamic',
         'fast-paced', 'salary', 'benefits', 'employer', 'employment', 'equal',
         'disability', 'veteran', 'race', 'religion', 'sex', 'discriminate',
         'discrimination', 'years', 'minimum', 'preferred', 'required', 'must',
         'needed', 'plus', 'experience', 'work', 'working', 'services',
         'communication', 'collaboration', 'sense', 'ownership', 'skills',
         'problem-solving', 'collaborate', 'closely', 'tool', 'tools', 'tooling',
         'cross-functional', 'lifecycle', 'job', 'posting', 'test', 'testing',
         'listing', 'vacancy', 'hiring', 'recruiter', 'recruitment', 'technical',
         'seeking', 'looking', 'ideal', 'solid', 'teams', 'growth', 'tooling',
         'email', 'cover', 'letter', 'interview', 'hr', 'practical', 'equivalent',
         'passionate', 'motivated', 'self-starter', 'detail-oriented', 'results-driven',
         'driven', 'innovative', 'creative', 'exceptional', 'outstanding', 'talented',
         'world-class', 'cutting-edge', 'industry-leading', 'top', 'best',
         'values', 'vision', 'workplace', 'colleagues', 'people', 'mission-driven',
         'color', 'origin', 'national', 'sexual', 'orientation', 'gender', 'identity',
         'protected', 'status', 'harassment', 'compliance', 'eligibility', 'eligible',
         'sponsorship', 'visa', 'science', 'systems',
         'ensure', 'ensuring', 'including', 'include', 'includes', 'help', 'helping',
         'support', 'supporting', 'using', "team's", 'understanding', 'write',
         ])
    return list(custom_words)


def jd_splitter(jd):
    text = re.sub(r'\n+', '\n', jd)
    clean_text = re.split(r'(?<=[-*•])\s+', text)

    lines = [line.replace('\n', ' ').rstrip('-–—•*') for line in clean_text]

    return lines


# utils for parser
def table_document(document):
    full_text = []
    if document.tables:
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        full_text.append(para.text)
        return full_text
    else:
        return False


def find_column_boundary(page, resolution=2, min_rows=3):
    words = page.extract_words()
    if not words:
        return None

    covered = np.zeros(int(page.width // resolution) + 1, dtype=bool)
    for w in words:
        start = int(w["x0"] // resolution)
        end = int(w["x1"] // resolution)
        covered[start: end + 1] = True

    mid_start = int(page.width * 0.3 // resolution)
    mid_end = int(page.width * 0.7 // resolution)
    gap_indices = [i for i in range(mid_start, mid_end) if not covered[i]]
    if not gap_indices:
        return None

    gap_idx = gap_indices[len(gap_indices) // 2]
    boundary = gap_idx * resolution

    left_words = [w for w in words if w["x1"] <= boundary]
    right_words = [w for w in words if w["x0"] >= boundary]

    def cluster_rows(word_list, tolerance=3):
        rows = []
        for w in sorted(word_list, key=lambda w: w["top"]):
            for row in rows:
                if abs(row["top"] - w["top"]) <= tolerance:
                    row["words"].append(w)
                    break
            else:
                rows.append({"top": w["top"], "words": [w]})
        return rows

    left_rows = cluster_rows(left_words)
    right_rows = cluster_rows(right_words)

    if len(left_rows) < min_rows or len(right_rows) < min_rows:
        return None

    return boundary
