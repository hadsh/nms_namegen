"""Candidate route readings, and the controls that make a negative mean something.

A candidate is a place in one of the two PRNG streams plus a way of reading
the word there. Per-body candidates are aggregated to "does any body fire?"
before scoring, because the corpus label is system-level.

The two controls matter more than the sweep. A search that finds nothing is
worth nothing unless it can be shown to find something that is really there,
so `control_uncharted` re-runs the whole sweep against a label whose reading
is already known and in the library, and `control_planted` re-runs it against
synthetic labels of exactly the per-body shape being hunted.
"""
import argparse
import sys

from score import best_threshold, constant_per_stratum, stratified
from trace import load, split, trace

sys.path.insert(0, "../..")
from nms_namegen.prng import PRNG
from nms_namegen.system import CONST_A, CONST_B, _probability

WORDS_PER_STREAM = 40


def words_from(seed, count):
    rng = PRNG(seed)
    out = []
    for _ in range(count):
        rng._updateSeed()
        out.append(rng.seed)
    return out


def _mix(value):
    value &= 0xFFFFFFFFFFFFFFFF
    value = ((value >> 33) ^ value) * CONST_A
    value &= 0xFFFFFFFFFFFFFFFF
    value = ((value >> 33) ^ value) * CONST_B
    value &= 0xFFFFFFFFFFFFFFFF
    return (value >> 33) ^ value


def _reseed_planet_name(seed):
    """How planetName() turns a body seed into a stream."""
    low = seed & 0xFFFFFFFF
    high = seed >> 32
    rol = ((low & 0x0000FFFF) << 16) | ((low & 0xFFFF0000) >> 16)
    rol = (rol ^ low ^ high) & 0xFFFFFFFF
    if low == 0:
        return ((low + 1) * PRNG.MULTIPLIER) + rol
    return (low * PRNG.MULTIPLIER) + rol


def _reseed_system(seed):
    """How systemAttributes() turns its 32-bit system seed into a stream."""
    low = seed & 0xFFFFFFFF
    rol = ((low & 0x0000FFFF) << 16) | ((low & 0xFFFF0000) >> 16)
    rol = (rol ^ low) & 0xFFFFFFFF
    if low == 0:
        return ((low + 1) * PRNG.MULTIPLIER) + rol
    return (low * PRNG.MULTIPLIER) + rol


def _reseed_planet_seeds(seed):
    """How planetSeeds() turns its 64-bit register into a stream."""
    value = seed & 0xFFFFFFFFFFFFFFFF
    high = (
        (((value & 0xFFFF0000) >> 16) | ((value & 0x0000FFFF) << 16))
        ^ (value & 0xFFFFFFFF)
        ^ (value >> 32)
    )
    return ((high or 1) << 32) | (value & 0xFFFFFFFF)


RESEEDS = {
    "plain": lambda seed: seed,
    "pname": _reseed_planet_name,
    "sys": _reseed_system,
    "plan": _reseed_planet_seeds,
    "mix": _mix,
    "mixplan": lambda seed: _reseed_planet_seeds(_mix(seed)),
}


def candidates(traced):
    """Every candidate reading for one system, as name -> score in [0,1).

    A lower score means "more likely dissonant", so a per-body candidate is
    aggregated with min: that is exactly "at least one body fired".
    """
    out = {}
    for name, word in traced["words"].items():
        if word is None:
            continue
        out["W:%s.lo" % name] = float(_probability(word))
        out["W:%s.hi" % name] = float(_probability(word >> 32))

    for name, seed in (
        ("sysStart", traced["sys_start_seed"]),
        ("sysTail", traced["sys_tail_seed"]),
        ("planStart", traced["planet_start_seed"]),
        ("planTail", traced["planet_tail_seed"]),
    ):
        for i, word in enumerate(words_from(seed, WORDS_PER_STREAM)):
            out["S:%s+%d.lo" % (name, i + 1)] = float(_probability(word))
            out["S:%s+%d.hi" % (name, i + 1)] = float(_probability(word >> 32))

    seeds = traced["ps"]["planet_seeds"]
    out["#bodies"] = -float(len(seeds))
    if seeds:
        for reseed_name, reseed in RESEEDS.items():
            columns = [[] for _ in range(WORDS_PER_STREAM)]
            for seed in seeds:
                for i, word in enumerate(words_from(reseed(seed), WORDS_PER_STREAM)):
                    columns[i].append(word)
            for i, column in enumerate(columns):
                out["B:%s+%d.lo" % (reseed_name, i + 1)] = min(
                    float(_probability(word)) for word in column)
                out["B:%s+%d.hi" % (reseed_name, i + 1)] = min(
                    float(_probability(word >> 32)) for word in column)
        out["B:raw.lo"] = min(float(_probability(seed)) for seed in seeds)
        out["B:raw.hi"] = min(float(_probability(seed >> 32)) for seed in seeds)
    pre = traced["pre_body_seeds"]
    if pre:
        out["B:pre.lo"] = min(float(_probability(seed)) for seed in pre)
        out["B:pre.hi"] = min(float(_probability(seed >> 32)) for seed in pre)
    return out


def prepare(rows):
    prepared = []
    for row in rows:
        traced = trace(int(row["sysaddress"], 16), row["galaxy_namegen"])
        prepared.append((candidates(traced), traced, row))
    return prepared


def run(prepared, label_of, title, top=15):
    scored = [(c, label_of(t, r)) for c, t, r in prepared]
    scored = [(c, l) for c, l in scored if l is not None]
    feats = [c for c, _ in scored]
    labels = [1 if l else 0 for _, l in scored]
    strata = [t["attrs"]["star_type"]
              for (c, t, r) in prepared if label_of(t, r) is not None]
    keys = sorted(set().union(*[set(f) for f in feats]))
    baseline = constant_per_stratum(labels, strata)
    results = []
    for key in keys:
        scores = [f.get(key, 1.0) for f in feats]
        results.append((stratified(scores, labels, strata)[0],
                        best_threshold(scores, labels)[0], key))
    results.sort(reverse=True)
    print("\n=== %s" % title)
    print("    n=%d  dissonant=%d  always-false=%.4f  star-type-only=%.4f  candidates=%d"
          % (len(labels), sum(labels), 1 - sum(labels) / len(labels), baseline, len(keys)))
    print("    %-24s %10s %10s" % ("candidate", "stratified", "flat"))
    for strat, flat, key in results[:top]:
        print("    %-24s %10.4f %10.4f" % (key, strat, flat))
    return results, baseline


def control_uncharted(prepared):
    """A reading that IS in the library, scored by the sweep from scratch.

    W:uncharted.lo is the exact word systemAttributes() compares against
    EMPTY_SYSTEM_THRESHOLD. If the sweep cannot put it on top, the sweep
    cannot find a route reading and a null result below proves nothing.
    """
    return run(prepared, lambda t, r: r.get("uncharted"),
               "CONTROL: the known `uncharted` reading", top=5)


def control_planted(prepared, reseed_name, index, modulus):
    """A synthetic label of exactly the shape being hunted.

    "Some body fired a 1-in-`modulus` draw at word `index` of its own
    stream" - a per-body overlay, aggregated to the system level the way the
    real label is. Recovering this at 1.0000 is what licenses reading a low
    score against the real label as absence rather than blindness.
    """
    reseed = RESEEDS[reseed_name]

    def planted(traced, row):
        for seed in traced["ps"]["planet_seeds"]:
            word = words_from(reseed(seed), index)[index - 1] & 0xFFFFFFFF
            if (word * modulus) >> 32 == 0:
                return True
        return False

    return run(prepared, planted,
               "CONTROL: planted any-body %s+%d rng(%d)==0"
               % (reseed_name, index, modulus), top=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()

    dev, _held = split(load())
    prepared = prepare(dev)

    control_uncharted(prepared)
    for reseed_name, index, modulus in (("pname", 3, 28), ("mix", 11, 28),
                                        ("plan", 1, 32), ("plain", 7, 20)):
        control_planted(prepared, reseed_name, index, modulus)
    if not args.controls_only:
        run(prepared, lambda t, r: r["label"], "dissonance (development set)", top=15)
