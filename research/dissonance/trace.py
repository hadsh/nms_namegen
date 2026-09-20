"""An instrumented copy of the generation route, used to find candidate reads.

`systemAttributes()` and `planetSeeds()` return what the library believes;
this returns the same thing plus the PRNG stream state at every point a draw
could be read from. It is a copy rather than an instrumentation hook so that
nothing in `nms_namegen/` has to change to run the search, and `selftest()`
asserts the copy still reproduces the library exactly on every labelled
system - a copy that has drifted would score candidates against the wrong
stream and every result below would be meaningless.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from nms_namegen.iprng import indexPrimedPRNG
from nms_namegen.prng import PRNG
from nms_namegen.region import voxelAttributes
from nms_namegen.system import (ABANDONED_SYSTEM_THRESHOLD, CONST_A, CONST_B,
                                EMPTY_SYSTEM_THRESHOLD, PIRATE_SYSTEM_THRESHOLD,
                                _bodySeed, _probability)


def trace(portal_code, galaxy):
    portal_code = portal_code & 0xFFFFFFFFFFF
    system_id = (portal_code & 0xFFF00000000) >> 32
    universalAddress = (((system_id << 8) | (galaxy & 0xFF)) << 32) | (
        portal_code & 0xFFFFFFFF
    )
    va = voxelAttributes(portal_code)
    system_id = system_id - 1
    system_seed = indexPrimedPRNG(universalAddress) & 0xFFFFFFFF
    rol16 = ((system_seed & 0x0000FFFF) << 16) | ((system_seed & 0xFFFF0000) >> 16)
    rol16 = (rol16 ^ system_seed) & 0xFFFFFFFF
    if system_seed == 0:
        seed = ((system_seed + 1) * PRNG.MULTIPLIER) + rol16
    else:
        seed = (system_seed * PRNG.MULTIPLIER) + rol16

    rng = PRNG(seed)
    star_type = 0
    safe_start = 0
    prime_planet_count = 2
    planet_count = 1
    anomaly = 0

    if system_id < va["guide_star_count"]:
        planet_count = (((seed & 0xFFFFFFFF) * 4) >> 0x20) + 3
        safe_start = rng.random(planet_count) + 1
    else:
        star_type = 0
        if (((seed & 0xFFFFFFFF) * 0x64) >> 0x20) < 0x1E:
            star_type = rng.random(3) + 1
        anomaly_diff = system_id - va["guide_star_count"]
        if va["black_hole_count"] > 0 and 0 <= anomaly_diff < va["black_hole_count"]:
            anomaly = 2
            star_type = 0
        if (
            va["atlas_station_count"] > 0
            and anomaly_diff - va["black_hole_count"] >= 0
            and anomaly_diff - va["black_hole_count"] < va["atlas_station_count"]
        ):
            anomaly = 1
            star_type = 0
        planet_count = rng.random(6) + 1
        if va["guide_star_renegade_count"] >= 10 or star_type != 0 or anomaly != 0:
            safe_start = 0
        else:
            safe_start = rng.random(planet_count + 1)

    rng._updateSeed()
    economy_word = rng.seed & 0xFFFFFFFF
    economy_type = {0: 4, 1: 6, 2: 1, 3: 5, 4: 2, 5: 3, 6: 7}[(economy_word * 7) >> 32]
    rng._updateSeed()
    wealth_word = rng.seed & 0xFFFFFFFF
    wealth_pct = (wealth_word * 100) >> 32
    wealth = {0: 3, 1: 1, 2: 2}[0 if wealth_pct < 10 else (1 if wealth_pct < 30 else 2)]
    rng._updateSeed()
    conflict_word = rng.seed & 0xFFFFFFFF
    conflict_level = {0: 1, 1: 2, 2: 3}[(conflict_word * 3) >> 32]
    rng._updateSeed()
    race_word = rng.seed & 0xFFFFFFFF
    dominant_race = {0: 1, 1: 3, 2: 2}[(race_word * 3) >> 32]

    if system_id < va["guide_star_renegade_count"]:
        star_type = rng.random(3) + 1
    if system_id > 0x3E7 and system_id < 0x429:
        star_type = 4

    rng._updateSeed()
    abandoned_word = rng.seed
    abandoned = bool(_probability(rng.seed) < ABANDONED_SYSTEM_THRESHOLD[star_type])
    uncharted = False
    uncharted_word = None
    if not abandoned:
        rng._updateSeed()
        uncharted_word = rng.seed
        uncharted = bool(_probability(rng.seed) < EMPTY_SYSTEM_THRESHOLD[star_type])
    if uncharted:
        dominant_race = 0
    if abandoned:
        wealth = 1
        conflict_level = 1

    diff = 6 - planet_count
    prime_word = None
    if diff < 1:
        prime_planet_count = 0
    else:
        prime_word = rng.seed
        if (rng.random(100) >= 33) or diff < 2:
            prime_planet_count = 1

    gas_giant = False
    if star_type == 4:
        prime_planet_count += planet_count
        planet_count = 0
        if rng.random(100) < 15:
            gas_giant = True
            if rng.random(100) < 66:
                planet_count = 0
                prime_planet_count = 6

    pirate = False
    if not abandoned and not uncharted and (star_type != 0 or safe_start <= 0):
        peek = PRNG(rng.seed)
        peek._updateSeed()
        pirate = bool(_probability(peek.seed) < PIRATE_SYSTEM_THRESHOLD[star_type])

    sys_tail_seed = rng.seed

    attrs = dict(
        planet_count=planet_count, prime_planet_count=prime_planet_count,
        safe_start_planet=safe_start, gas_giant=gas_giant, star_type=star_type,
        economy_type=economy_type, wealth=wealth, conflict_level=conflict_level,
        dominant_race=dominant_race, uncharted=uncharted, abandoned=abandoned,
        pirate=pirate,
    )

    galacticCoords = portal_code & 0xFFFFFFFF
    systemIndex = ((portal_code & 0x0FFF00000000) >> 24) | galaxy
    moon_count = 0
    register = (systemIndex << 0x20) | galacticCoords
    register = ((register >> 33) ^ register) * CONST_A
    register &= 0xFFFFFFFFFFFFFFFF
    register = ((register >> 33) ^ register) * CONST_B
    register &= 0xFFFFFFFFFFFFFFFF
    register = (register >> 33) ^ register
    seed_h = (
        (((register & 0xFFFF0000) >> 16) | ((register & 0x0000FFFF) << 16))
        ^ (register & 0xFFFFFFFF)
        ^ (register >> 32)
    )
    seed_l = register & 0xFFFFFFFF
    if seed_h == 0:
        seed_h = 1
    planet_start_seed = seed_h << 32 | seed_l
    prng = PRNG(planet_start_seed)

    primary_count = planet_count
    total_count = primary_count + prime_planet_count
    stop = safe_start - 1
    planet_seeds = []
    sizes = []
    pre_body_seeds = []

    if gas_giant:
        for _ in range(total_count):
            pre_body_seeds.append(prng.seed)
            planet_seeds.append(_bodySeed(prng))
        ps = dict(planet_seeds=planet_seeds, planet_count=1,
                  moon_count=total_count - 1, sizes=sizes)
    else:
        i = 0
        while i < primary_count:
            i += 1
            size = prng.random(3)
            sizes.append(size)
            if size == 0:
                m = primary_count - i
                m = 0 if m < 0 else (2 if m > 2 else m)
                n_moons = prng.random(m + 1)
                if n_moons > 0:
                    while i != stop:
                        i += 1
                        n_moons -= 1
                        moon_count += 1
                        if n_moons <= 0:
                            break
        i = 0
        while i < primary_count:
            pre_body_seeds.append(prng.seed)
            planet_seeds.append(_bodySeed(prng))
            i += 1
        while i < total_count:
            size = prng.random(3)
            sizes.append(size)
            pre_body_seeds.append(prng.seed)
            planet_seeds.append(_bodySeed(prng))
            i += 1
            if size == 0:
                m = total_count - i
                m = 0 if m < 0 else (2 if m > 2 else m)
                n_moons = prng.random(m + 1)
                while n_moons > 0 and i != stop:
                    pre_body_seeds.append(prng.seed)
                    planet_seeds.append(_bodySeed(prng))
                    moon_count += 1
                    n_moons -= 1
                    i += 1
        ps = dict(planet_seeds=planet_seeds, planet_count=total_count - moon_count,
                  moon_count=moon_count, sizes=sizes)

    return dict(
        attrs=attrs, ps=ps,
        sys_start_seed=seed, sys_tail_seed=sys_tail_seed,
        planet_start_seed=planet_start_seed, planet_tail_seed=prng.seed,
        pre_body_seeds=pre_body_seeds,
        words=dict(economy=economy_word, wealth=wealth_word, conflict=conflict_word,
                   race=race_word, abandoned=abandoned_word, uncharted=uncharted_word,
                   prime=prime_word),
    )


def load():
    """The labelled set, built by build_corpus.py."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "joined.json")
    if not os.path.exists(path):
        raise SystemExit("run build_corpus.py first")
    with open(path) as fh:
        return json.load(fh)


def split(rows):
    """A fixed 80/20 split, keyed on the address so it never moves.

    The held-out fifth is looked at once, at the end. The failure mode this
    guards against is not a lucky candidate - at n=1002 that is impossible -
    but a rule quietly adjusted until it fits.
    """
    dev, held = [], []
    for row in rows:
        key = "%s|%d" % (row["sysaddress"].upper(), row["galaxy_namegen"])
        digest = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
        (held if digest % 5 == 0 else dev).append(row)
    return dev, held


def selftest(rows):
    """Assert this copy still matches the library it was copied from."""
    from nms_namegen.system import planetSeeds, systemAttributes

    for row in rows:
        portal_code = int(row["sysaddress"], 16)
        galaxy = row["galaxy_namegen"]
        traced = trace(portal_code, galaxy)
        attrs = systemAttributes(portal_code, galaxy)
        seeds = planetSeeds(portal_code, galaxy)
        for key, value in attrs.items():
            assert traced["attrs"][key] == value, (row["sysaddress"], key)
        assert traced["ps"]["planet_seeds"] == seeds["planet_seeds"], row["sysaddress"]
        assert traced["ps"]["moon_count"] == seeds["moon_count"], row["sysaddress"]
    return len(rows)


if __name__ == "__main__":
    print("trace() matches the library on %d systems" % selftest(load()))
