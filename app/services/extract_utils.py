import numpy as np


def table_document(document):
    if document.tables:
        full_text = []
        if document.tables:
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text.append(cell.text)
        return "\n".join(full_text)
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
        covered[start : end + 1] = True

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
