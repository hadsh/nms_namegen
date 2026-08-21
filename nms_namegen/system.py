from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
from nms_namegen.iprng import indexPrimedPRNG
from nms_namegen.region import voxelAttributes
from nms_namegen.roman import toRoman
import numpy as np

TINY_DOUBLE = np.double(2.3283064370807974e-10)

CONST_A = 0x64DD81482CBD31D7
CONST_B = 0xE36AA5C613612997

# abandonedSystemProbability * 100, indexed by star type (yellow, green, blue,
# red, purple), from the original disassembly transcription (upstream 160de15).
ABANDONED_SYSTEM_PCT = [0, 10, 10, 0, 35]


# Returns a system name for No Man's Sky
#
# Parameters:
#   Portal code as a hexadecimal integer,
#   in the format 0xPSSSYYZZZXXX
#   Where P - Planet id (unused)
#   SSS - System Id
#   YY - Y coordinate
#   ZZZ - Z coordinate
#   XXX - X coordinate
#
#   Galaxy is the galaxy number starting with Euclid as 0.
#
def systemName(portal_code, galaxy):
    galacticCoords = portal_code & 0xFFFFFFFF
    systemIndex = ((portal_code & 0x0FFF00000000) >> 24) | galaxy

    rolCoords = ((galacticCoords & 0x0000FFFF) << 16) | (
        (galacticCoords & 0xFFFF0000) >> 16
    )
    rolCoords = (rolCoords ^ galacticCoords ^ systemIndex) & 0xFFFFFFFF

    seed = 0
    if galacticCoords == 0:
        seed = ((galacticCoords + 1) * PRNG.MULTIPLIER) + rolCoords
    else:
        seed = (galacticCoords * PRNG.MULTIPLIER) + rolCoords

    rng = PRNG(seed)

    alphaset_index = 0x00
    alphaset_reg = ((seed & 0xFFFFFFFF) * 0x5) >> 32
    if alphaset_reg == 0:
        alphaset_index = 0x02
    else:
        if (alphaset_reg & 0xFF) < 0x04:
            alphaset_index = (alphaset_reg & 0xFF) + 0x02
        else:
            alphaset_index = 0x07

    max_length = rng.random(4) + 0x06
    name = generateName(rng, alphaset_index, 6, max_length)
    name = name.capitalize()

    # Hyphenated names
    if len(name) < 8:
        r = rng.random(4)
        if r < 2:
            alphaset_reg = rng.random(5)
            min_length = 3
            max_length = 5

            if alphaset_reg == 0:
                alphaset_index = 0x02
            else:
                if alphaset_reg < 4:
                    alphaset_index = alphaset_reg + 2
                else:
                    alphaset_index = 0x07

            name2 = generateName(rng, alphaset_index, min_length, max_length)
            name = f"{name}-{name2.capitalize()}"

    # Might have to tune the rng parameter here.
    # I'm not sure where the cutoff actually as yet
    if rng.random(0x0A) < 0x03:
        n = (rng.random(19)) + 1
        if n > 19:
            n = 19

        name = f"{name} {toRoman(n)}"
    return name


# Returns a dictionary containing planet counts for a system.
def systemAttributes(portal_code, galaxy):
    portal_code = portal_code & 0xFFFFFFFFFFF
    system_id = (portal_code & 0xFFF00000000) >> 32
    universalAddress = (((system_id << 8) | (galaxy & 0xFF)) << 32) | (
        portal_code & 0xFFFFFFFF
    )
    # print("UA:", hex(universalAddress))
    va = voxelAttributes(portal_code)
    # Restored from the original disassembly transcription (upstream commit
    # 160de15, dropped in the "Cleaned up system code" commit): the game
    # decrements the system id before every branch comparison below (the
    # universal address above uses the raw id). Corpus-verified: with the
    # anomaly restoration this fixes 12 mispredicted boundary systems and
    # breaks none (McNemar p=0.0002, n=1676 labelled systems).
    system_id = system_id - 1
    system_seed = indexPrimedPRNG(universalAddress) & 0xFFFFFFFF
    # print("system seed: ", hex(system_seed))
    rol16 = ((system_seed & 0x0000FFFF) << 16) | ((system_seed & 0xFFFF0000) >> 16)
    rol16 = (rol16 ^ system_seed) & 0xFFFFFFFF
    seed = 0
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

        # Restored from the original disassembly transcription (upstream
        # commit 160de15): black-hole and Atlas-station system ids are
        # anomalies; they force star_type to 0 and, via the condition below,
        # skip the safe_start draw. Dropping this shifted every subsequent
        # RNG draw for those systems.
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
            # The draw spans 0..planet_count, not 0..planet_count+1: this is
            # the internal class limit that bounds moon insertion below, and
            # it can never exceed the number of primary bodies. Corpus-
            # verified on records discovered in 2025 or later (see the note
            # above planetSeeds): +5.0 pt on 1,041 purple systems, -0.1 pt on
            # 7,314 Euclid systems (8 records, noise).
            safe_start = rng.random(planet_count + 1)

    # These 4 draws were previously discarded (bare _updateSeed() calls, one
    # _updateSeed() per slot either way so the stream position for everything
    # below is unchanged). Formulas and category numbering were derived by
    # brute-force search against a corpus of community-labelled systems
    # (economy, wealth, conflict and race, read off the in-game infobox).
    # The category numbers below (1-7 economy, 1-3 wealth/conflict/race) are
    # this library's own convention.
    rng._updateSeed()
    economy_word = rng.seed & 0xFFFFFFFF
    # 7-way draw, permutation found by brute-force best-match against 7964
    # labelled economy codes: 94.76% agreement.
    economy_type = {0: 4, 1: 6, 2: 1, 3: 5, 4: 2, 5: 3, 6: 7}[(economy_word * 7) >> 32]

    rng._updateSeed()
    wealth_word = rng.seed & 0xFFFFFFFF
    # Percentage draw (not a plain 3-way mulhi - that scored only 49.62% on
    # the same corpus), 10%/30% cutoffs, 97.82% agreement on 12929 rows.
    wealth_pct = (wealth_word * 100) >> 32
    wealth_bucket = 0 if wealth_pct < 10 else (1 if wealth_pct < 30 else 2)
    wealth = {0: 3, 1: 1, 2: 2}[wealth_bucket]

    rng._updateSeed()
    conflict_word = rng.seed & 0xFFFFFFFF
    # 3-way draw, identity mapping, 97.30% agreement on 9246 rows (pirate
    # systems, category 4, excluded from this corpus check - not modeled).
    conflict_level = {0: 1, 1: 2, 2: 3}[(conflict_word * 3) >> 32]

    rng._updateSeed()
    race_word = rng.seed & 0xFFFFFFFF
    # 3-way draw, 94.78% agreement on 11325 rows (uncharted/abandoned
    # locals codes excluded from this corpus check - no race to predict).
    dominant_race = {0: 1, 1: 3, 2: 2}[(race_word * 3) >> 32]

    if system_id < va["guide_star_renegade_count"]:
        star_type = rng.random(3) + 1

    # Purple window: raw SSI 0x3E9-0x429 INCLUSIVE (system_id here is already
    # decremented). Verified on 1,316 purple systems across 52 galaxies: the
    # edge ids 0x3E9, 0x3EA and 0x429 are 100% purple; both the old exclusive
    # window and the upstream (undecremented) one missed edge ids.
    if system_id > 0x3E7 and system_id < 0x429:  # Purple
        star_type = 4

    # Abandoned-system check (probability per star type from the original
    # disassembly transcription: [0, .10, .10, 0, .35]). When a system is
    # abandoned, the empty-system draw is SKIPPED, shifting every subsequent
    # draw back one slot. Derived from 1,091 ground-truth purple systems:
    # the gas-giant gate below only aligns across the corpus under this
    # conditional skip (precision 79%/recall 97% vs 65%/70% without it), and
    # it also lifts green/red (star types 1/2) planet accuracy 92.9->93.9%
    # across the rest of the corpus.
    abandoned = rng.random(100) < ABANDONED_SYSTEM_PCT[star_type]
    if not abandoned:
        rng._updateSeed()  # empty-system check

    diff = 6 - planet_count
    if diff < 1:
        prime_planet_count = 0
    elif (rng.random(100) >= 33) or diff < 2:
        prime_planet_count = 1

    # Purple systems take a separate route. Every body is re-labelled as an
    # extra body (prime_planet_count carries the whole count, planet_count
    # drops to 0), so planetSeeds() classifies them all through its extra
    # loop instead of the primary one. Then two nested draws: the first, at
    # 15%, switches the system to the gas-giant layout (one giant plus moons,
    # see planetSeeds); the second, at 66% of those, forces the body count to
    # the maximum of six, which is where the (1 planet, 5 moons) systems come
    # from. The second draw is nested, not mutually exclusive: reading it as
    # an alternative branch consumed a draw on the wrong systems and desynced
    # the stream. This route and the extra-body loop in planetSeeds carry
    # essentially the whole purple fix between them; neither is worth much
    # alone. Corpus-verified on 1,041 purple systems discovered in 2025 or
    # later: planet counts 58.1% -> 94.1%, gas-giant precision 80.3% ->
    # 94.7% (recall 98.4% -> 95.7%).
    gas_giant = False
    if star_type == 4:
        prime_planet_count += planet_count
        planet_count = 0
        if rng.random(100) < 15:
            gas_giant = True
            if rng.random(100) < 66:
                planet_count = 0
                prime_planet_count = 6

    return {
        "planet_count": planet_count,
        "prime_planet_count": prime_planet_count,
        "safe_start_planet": safe_start,
        # Gas-giant layout: the system renders as a single giant planet
        # orbited by every other body as a moon (see planetSeeds). Purple
        # systems only.
        "gas_giant": gas_giant,
        # Star colour class, validated empirically against labelled
        # spectral classes (80-99% agreement):
        # 0 -> yellow/white (F/G, base), 1 -> green (E, Emeril),
        # 2 -> blue (B/O, Indium), 3 -> red (K/M, Cadmium),
        # 4 -> purple/exotic (X/Y, system_id 0x3E8-0x428).
        "star_type": star_type,
        # Economy category, 1-7 (1=trading, 2=advanced materials,
        # 3=scientific, 4=mining, 5=manufacturing, 6=technology, 7=power
        # generation). Validated 94.76% (7964 systems), see the derivation
        # comment above.
        "economy_type": economy_type,
        # Wealth tier, 1-3 (1=low, 2=medium, 3=high). Validated 97.82%
        # (12929 systems).
        "wealth": wealth,
        # Conflict level, 1-3 (1=low, 2=medium, 3=high). Pirate systems
        # (a separate mechanic, not modeled here) are excluded. Validated
        # 97.30% (9246 systems, pirate rows excluded from that corpus check).
        "conflict_level": conflict_level,
        # Dominant race, 1-3 (1=gek, 2=korvax, 3=vy'keen). Uncharted/
        # abandoned-without-race locals codes are not modeled here.
        # Validated 94.78% (11325 systems, those rows excluded).
        "dominant_race": dominant_race,
    }

# Corpus figures quoted in this module are measured only against community
# records discovered in 2025 or later. The game has regenerated its universe
# several times, most visibly at the Origins update, and older records
# describe a universe this generator no longer produces: single-body systems
# are 7.1% of pre-2021 records and 0.2% of 2025+ ones, and body counts match
# at 59% on pre-2021 records against 95% on recent ones. Measuring against
# the whole corpus therefore scores the archive, not the generator.
def planetSeeds(portal_code, galaxy):
    system_attributes = systemAttributes(portal_code, galaxy)

    # Gas-giant layout: one giant plus moons. Every record still gets a seed
    # so per-index name lookups keep working, but no class is drawn - the
    # layout is fixed, so the class draws are not in the stream either.
    gas_giant = system_attributes.get("gas_giant", False)

    planet_seeds = []
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

    seed = seed_h << 32 | seed_l
    rng = PRNG(seed)

    primary_count = system_attributes["planet_count"]
    total_count = primary_count + system_attributes["prime_planet_count"]
    # The system holds total_count bodies, no more: every moon placed below
    # takes one of those slots away from the planets. safe_start_planet is
    # the internal class limit, and placement stops one slot before it.
    stop = system_attributes["safe_start_planet"] - 1

    # Per-slot size class (0-2), one draw per classified body. EXPERIMENTAL:
    # exposed for a future planet-size/diameter feature, but NOT validated at
    # the per-slot level yet - a system-level sanity check (predicted
    # moon_count vs an independently observed moon count) shows a
    # real but modest correlation (62.67% exact match, 3584 systems), well
    # below the 94-98% bar economy/wealth/conflict/star_type cleared - likely
    # because the per-slot generation order here is not known to match the
    # order the game displays bodies in. Do not treat "sizes" as validated
    # until that ordering question is resolved. Inserted moons carry no draw
    # of their own, so they contribute no entry here.
    sizes = []

    if gas_giant:
        for _ in range(total_count):
            planet_seeds.append(_bodySeed(rng))
        return {
            "planet_seeds": planet_seeds,
            "planet_count": 1,
            "moon_count": total_count - 1,
            "sizes": sizes,
        }

    # Primary bodies: all classes first, then all seeds. A size-0 body is a
    # large planet and pulls 0-2 moons in behind it, each taking the next
    # slot.
    i = 0
    while i < primary_count:
        i += 1
        size = rng.random(3)
        sizes.append(size)

        if size == 0:
            m = primary_count - i
            if m < 0:
                m = 0
            if m > 2:
                m = 2

            n_moons = rng.random(m + 1)
            # Accumulate: each large planet rolls its own moons, a plain
            # assignment here let the last roll erase the previous ones.
            # Only count moons actually placed: the placement loop can exit
            # immediately (i already on the stop slot) without placing any,
            # and crediting the raw roll skewed the planet/moon split
            # (2490 labelled systems: pair-match 68.9% -> 73.0%).
            if n_moons > 0:
                while i != stop:
                    i += 1
                    n_moons -= 1
                    moon_count += 1
                    if n_moons <= 0:
                        break

    i = 0
    while i < primary_count:
        planet_seeds.append(_bodySeed(rng))
        i += 1

    # Extra bodies. Unlike the primary bodies above, these interleave class
    # and seed per record, and each of them can pull its own moons in: the
    # earlier version drew the seed first, then a class it only used to burn
    # a draw, and never converted an extra body into a moon at all. Corpus-
    # verified: +0.6 pt on 7,314 Euclid systems, and on purple systems -
    # where this loop now classifies every body - planet counts go from
    # 59.8% to 94.1% (1,041 systems). Both figures are on records discovered
    # in 2025 or later, see the note above planetSeeds.
    while i < total_count:
        size = rng.random(3)
        sizes.append(size)
        planet_seeds.append(_bodySeed(rng))
        i += 1

        if size == 0:
            m = total_count - i
            if m < 0:
                m = 0
            if m > 2:
                m = 2

            n_moons = rng.random(m + 1)
            while n_moons > 0 and i != stop:
                planet_seeds.append(_bodySeed(rng))
                moon_count += 1
                n_moons -= 1
                i += 1

    return {
        "planet_seeds": planet_seeds,
        "planet_count": total_count - moon_count,
        "moon_count": moon_count,
        # EXPERIMENTAL, not validated at the per-slot level - see comment
        # where "sizes" is built above.
        "sizes": sizes,
    }


# Mixes the next two PRNG words into one body seed.
def _bodySeed(rng):
    low = rng.randi() & 0xFFFFFFFF
    high = rng.randi() & 0xFFFFFFFF

    register = (high << 0x20) | low
    register = ((register >> 33) ^ register) * CONST_A
    register &= 0xFFFFFFFFFFFFFFFF
    register = ((register >> 33) ^ register) * CONST_B
    register &= 0xFFFFFFFFFFFFFFFF
    return (register >> 33) ^ register
