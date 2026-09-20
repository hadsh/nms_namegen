"""Scoring primitives.

Two details here are not incidental; the `uncharted` control in sweep.py
fails without either of them, which is how they were found.

Thresholds are only ever placed between distinct score values. A sweep that
walks tied scores one at a time can split a tie in an order no threshold
could reproduce, which lets a *constant* candidate score 100%.

Thresholds are fitted per star type. Every probability gate the route
actually contains is a per-star-type table (see EMPTY_SYSTEM_THRESHOLD in
nms_namegen/system.py), so a candidate that is only allowed one global
threshold cannot express a real reading even when it has found one.
"""


def best_threshold(scores, labels):
    """Best agreement over `score <= t`, and the t that achieves it."""
    n = len(scores)
    if n == 0:
        return 1.0, None
    order = sorted(range(n), key=lambda i: scores[i])
    correct = n - sum(labels)
    best = (correct, None)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        for k in range(i, j + 1):
            correct += 1 if labels[order[k]] else -1
        if correct > best[0]:
            best = (correct, scores[order[j]])
        i = j + 1
    return best[0] / n, best[1]


def stratified(scores, labels, strata):
    """Fit one threshold per stratum. Returns pooled agreement and thresholds."""
    groups = {}
    for score, label, key in zip(scores, labels, strata):
        groups.setdefault(key, ([], []))
        groups[key][0].append(score)
        groups[key][1].append(label)
    correct = 0
    thresholds = {}
    for key, (group_scores, group_labels) in groups.items():
        agreement, threshold = best_threshold(group_scores, group_labels)
        correct += round(agreement * len(group_scores))
        thresholds[key] = threshold
    return correct / len(scores), thresholds


def apply_stratified(scores, labels, strata, thresholds):
    tp = fp = fn = tn = 0
    for score, label, key in zip(scores, labels, strata):
        threshold = thresholds.get(key)
        predicted = threshold is not None and score <= threshold
        if predicted and label:
            tp += 1
        elif predicted:
            fp += 1
        elif label:
            fn += 1
        else:
            tn += 1
    n = tp + fp + fn + tn
    return dict(
        agreement=(tp + tn) / n,
        precision=tp / (tp + fp) if tp + fp else float("nan"),
        recall=tp / (tp + fn) if tp + fn else float("nan"),
        tp=tp, fp=fp, fn=fn, tn=tn, n=n,
    )


def constant_per_stratum(labels, strata):
    """Best agreement from predicting a constant within each stratum.

    This is the number every candidate has to beat. On this corpus it is not
    small, because star colour is confounded with the label by construction:
    the positives are a full pool and the negatives a per-colour capped
    sample, so star type carries selection, not signal.
    """
    cells = {}
    for label, key in zip(labels, strata):
        cells.setdefault(key, [0, 0])
        cells[key][label] += 1
    return sum(max(cell) for cell in cells.values()) / len(labels)
