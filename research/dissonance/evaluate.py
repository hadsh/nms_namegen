"""The one look at the held-out fifth, and the same rules at true prevalence.

The joined set is 57% dissonant only because it pools a full pool of
positives with a per-colour capped sample of negatives. Agreement on it is
therefore not comparable to anything. The balanced corpus on its own is the
only unbiased view, and at its real 15.7% prevalence the question is simply
whether any candidate beats always-predict-false. None does.
"""
import json
import os
import sys

from score import apply_stratified, stratified
from sweep import candidates, prepare
from trace import load, split, trace

sys.path.insert(0, "../..")

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "test", "fixtures")
# The best candidates the development sweep produced, in its own order.
BEST = ["S:sysStart+9.hi", "#bodies", "B:plain+35.hi"]


def columns(prepared):
    return ([c for c, _, _ in prepared],
            [1 if r["label"] else 0 for _, _, r in prepared],
            [t["attrs"]["star_type"] for _, t, _ in prepared])


def main():
    dev, held = split(load())
    dev_f, dev_l, dev_s = columns(prepare(dev))
    held_f, held_l, held_s = columns(prepare(held))

    n, npos = len(held_l), sum(held_l)
    print("HELD-OUT  n=%d  dissonant=%d  clean=%d" % (n, npos, n - npos))
    print("  %-30s agreement %.4f   precision  --      recall 0.0000"
          % ("always-predict-false", (n - npos) / n))

    cells = {}
    for label, star in zip(dev_l, dev_s):
        cells.setdefault(star, [0, 0])
        cells[star][label] += 1
    predict = {star: cell[1] > cell[0] for star, cell in cells.items()}
    tp = fp = fn = tn = 0
    for label, star in zip(held_l, held_s):
        if predict.get(star, False):
            tp, fp = tp + (label == 1), fp + (label == 0)
        else:
            fn, tn = fn + (label == 1), tn + (label == 0)
    print("  %-30s agreement %.4f   precision %.4f  recall %.4f"
          % ("star type only (no candidate)", (tp + tn) / n,
             tp / (tp + fp) if tp + fp else float("nan"),
             tp / (tp + fn) if tp + fn else float("nan")))

    for key in BEST:
        dev_agreement, thresholds = stratified(
            [f.get(key, 1.0) for f in dev_f], dev_l, dev_s)
        stats = apply_stratified(
            [f.get(key, 1.0) for f in held_f], held_l, held_s, thresholds)
        print("  %-30s agreement %.4f   precision %.4f  recall %.4f   (dev %.4f)"
              % (key, stats["agreement"], stats["precision"], stats["recall"],
                 dev_agreement))

    with open(os.path.join(FIXTURES, "nms-systems-ground-truth-2026-08-23.json")) as fh:
        balanced = json.load(fh)["systems"]
    unbiased = [dict(row, label=row["dissonant"]) for row in balanced
                if row.get("star_color") != "Purple"
                and isinstance(row.get("dissonant"), bool)]
    un_f, un_l, un_s = columns(prepare(unbiased))
    n, npos = len(un_l), sum(un_l)
    print("\nTRUE PREVALENCE (balanced corpus, non-purple)  n=%d  dissonant=%d (%.1f%%)"
          % (n, npos, 100 * npos / n))
    print("  %-30s agreement %.4f" % ("always-predict-false", (n - npos) / n))
    for key in BEST:
        _, thresholds = stratified([f.get(key, 1.0) for f in dev_f], dev_l, dev_s)
        stats = apply_stratified([f.get(key, 1.0) for f in un_f], un_l, un_s, thresholds)
        fitted, _ = stratified([f.get(key, 1.0) for f in un_f], un_l, un_s)
        print("  %-30s agreement %.4f   precision %.4f  recall %.4f"
              "   (refitted on this corpus: %.4f)"
              % (key, stats["agreement"], stats["precision"], stats["recall"], fitted))


if __name__ == "__main__":
    main()
