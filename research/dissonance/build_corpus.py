"""Join the two ground-truth fixtures into one labelled, non-purple set.

Positives come from the dissonant-only corpus, which carries no `false` rows
at all. Negatives can therefore only come from the balanced corpus, and only
where `dissonant` is literally False: a null there means the field was not
recorded, never that the system is clean.

Purple is excluded on both sides. Purple systems are 96% dissonant (187/194)
and the window that makes them purple is a plain address range, so including
them would measure that window rather than anything about dissonance.
"""
import json
import os
import sys

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "test", "fixtures")
POSITIVES = "nms-dissonant-non-purple-ground-truth-2026-09-18.json"
NEGATIVES = "nms-systems-ground-truth-2026-08-23.json"


def _key(row):
    return (row["sysaddress"].upper(), row["galaxy_namegen"])


def build():
    with open(os.path.join(FIXTURES, POSITIVES)) as fh:
        positives = json.load(fh)["systems"]
    with open(os.path.join(FIXTURES, NEGATIVES)) as fh:
        negatives = json.load(fh)["systems"]

    rows = {}
    for row in positives:
        assert row["dissonant"] is True
        assert row["star_color"] != "Purple"
        assert row["post_origins"]
        rows[_key(row)] = dict(row, label=True)

    for row in negatives:
        if row.get("star_color") == "Purple":
            continue
        if not isinstance(row.get("dissonant"), bool):
            continue
        key = _key(row)
        if row["dissonant"]:
            # Every non-purple positive in the balanced corpus must already be
            # in the dissonant corpus; if one is not, the two disagree about
            # which systems exist and neither can be trusted as a scoreboard.
            assert key in rows, "positive missing from the dissonant corpus: %r" % (key,)
            continue
        if key in rows:
            raise SystemExit("contradiction between the two corpora: %r" % (key,))
        rows[key] = dict(row, label=False)

    return list(rows.values())


if __name__ == "__main__":
    data = build()
    npos = sum(row["label"] for row in data)
    print("%d systems, %d dissonant, %d clean" % (len(data), npos, len(data) - npos))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "joined.json"), "w") as fh:
        json.dump(data, fh)
