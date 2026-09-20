"""The same search over boolean readings instead of thresholds.

A threshold on a probability expresses "the draw came in under p", which is
the shape of every gate the route actually has. It cannot express
`rng.random(N) == k` for k > 0, or a single-bit test, or a per-body rule that
needs every body to fire rather than any. This covers those, at the cost of
being slow: about 161k candidates and three minutes.

Scored as the gain over the star-type-only baseline, because that baseline
uses no candidate at all and star colour is confounded with the label by
construction.
"""
import sys

from sweep import RESEEDS, words_from
from trace import load, split, trace

sys.path.insert(0, "../..")

MODULI = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 20, 24, 25, 28, 30, 32,
          40, 50, 64, 100, 128, 200, 256]
WORDS_PER_STREAM = 24


def _readings(word, tag, out):
    low = word & 0xFFFFFFFF
    for modulus in MODULI:
        value = (low * modulus) >> 32
        for k in range(min(modulus, 4)):
            out["%s|r%d==%d" % (tag, modulus, k)] = value == k
        if modulus > 4:
            out["%s|r%d==last" % (tag, modulus)] = value == modulus - 1
    for bit in range(32):
        out["%s|bit%d" % (tag, bit)] = bool(low >> bit & 1)


def readings_for(traced):
    out = {}
    for name, word in traced["words"].items():
        if word is not None:
            _readings(word, "W:%s" % name, out)
    for name, seed in (("sysStart", traced["sys_start_seed"]),
                       ("sysTail", traced["sys_tail_seed"]),
                       ("planStart", traced["planet_start_seed"]),
                       ("planTail", traced["planet_tail_seed"])):
        for i, word in enumerate(words_from(seed, WORDS_PER_STREAM)):
            _readings(word, "S:%s+%d" % (name, i + 1), out)
            _readings(word >> 32, "S:%s+%dh" % (name, i + 1), out)

    seeds = traced["ps"]["planet_seeds"]
    if not seeds:
        return out
    per_body = []
    for seed in seeds:
        body = {}
        _readings(seed, "B:raw", body)
        _readings(seed >> 32, "B:rawh", body)
        for reseed_name, reseed in RESEEDS.items():
            for i, word in enumerate(words_from(reseed(seed), WORDS_PER_STREAM)):
                _readings(word, "B:%s+%d" % (reseed_name, i + 1), body)
                _readings(word >> 32, "B:%s+%dh" % (reseed_name, i + 1), body)
        per_body.append(body)
    for key in per_body[0]:
        values = [body[key] for body in per_body]
        out[key + "#any"] = any(values)
        out[key + "#all"] = all(values)
        out[key + "#first"] = values[0]
    return out


def main():
    dev, _held = split(load())
    data = []
    for row in dev:
        traced = trace(int(row["sysaddress"], 16), row["galaxy_namegen"])
        data.append((readings_for(traced), 1 if row["label"] else 0,
                     traced["attrs"]["star_type"]))

    n = len(data)
    cells = {}
    for _, label, star in data:
        cells.setdefault(star, [0, 0])
        cells[star][label] += 1
    baseline = sum(max(cell) for cell in cells.values()) / n

    keys = sorted(set().union(*[set(d[0]) for d in data]))
    results = []
    for key in keys:
        counts = {}
        for readings, label, star in data:
            value = readings.get(key, False)
            counts.setdefault(star, {(False, 0): 0, (False, 1): 0,
                                     (True, 0): 0, (True, 1): 0})
            counts[star][(value, label)] += 1
        # each star type may read the candidate either way round
        correct = sum(max(c[(True, 1)] + c[(False, 0)], c[(True, 0)] + c[(False, 1)])
                      for c in counts.values())
        results.append((correct / n, key))
    results.sort(reverse=True)

    print("boolean sweep: n=%d  star-type-only=%.4f  candidates=%d"
          % (n, baseline, len(keys)))
    for agreement, key in results[:20]:
        print("  %.4f  (+%.4f)  %s" % (agreement, agreement - baseline, key))


if __name__ == "__main__":
    main()
