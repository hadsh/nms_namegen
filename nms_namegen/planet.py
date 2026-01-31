from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
from nms_namegen.system import systemAttributes
import numpy as np
import roman

CONST_A = 0x64DD81482CBD31D7
CONST_B = 0xE36AA5C613612997

adornments = [
    "Prime",
    "Major",
    "Minor",
    "Alpha",
    "Beta",
    "Gamma",
    "Delta",
    "Omega",
    "Sigma",
    "Tau",
]

styles = [
    "%PROCNORM%",
    "%PROCNORM% %ADORNMENT%",
    "%PROCNORM% %NUMERAL%",
    "%PROCNORM% %SHORTCODE%",
    "%PROCLONG% %PROCSHORT%",
    "%PROCSHORT% %LONGCODE%",
    "New %PROCNORM%",
    "%PROCNORM% %ADORNMENT%",
    "%PROCNORM% %NUMERAL%",
    "Style 9",
    "New %PROCNORM%",  # Check this
]

TINY_DOUBLE = np.double(2.3283064370807974e-10)


# Need to work out how to get n_planets and n_prime_planets from the
# generator. n_prime_planets is either 1 or 0.
def planetSeed(portal_code, galaxy):
    system_attributes = systemAttributes(portal_code, galaxy)

    planet_seeds = []
    galacticCoords = portal_code & 0xFFFFFFFF
    systemIndex = ((portal_code & 0x0FFF00000000) >> 24) | galaxy
    planet_id = (portal_code & 0xF00000000000) >> 44

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

    i = 0
    planet_count = 0

    while i < system_attributes["planet_count"]:
        i += 1  # next index
        size = rng.random(3)
        # print(size)
        planet_count += 1  # count

        if size == 0:
            # This is a large planet
            # Add 1 or 2 moons.
            m = system_attributes["planet_count"] - i
            if m < 0:
                m = 0
            if m > 2:
                m = 2

            n_moons = rng.random(m + 1)
            # print("moons", n_moons)
            if n_moons > 0:
                # rcx_25 = &lOutput_1->maiPlanetParentIndices.maArray[planet_count];
                while i != system_attributes["safe_start_planet"] - 1:
                    # print(3)
                    i += 1
                    # set index to i_2
                    planet_count += 1  # add one to count
                    n_moons -= 1
                    if n_moons <= 0:
                        break

    i = 0
    while i < system_attributes["planet_count"]:
        low = rng.randi() & 0xFFFFFFFF
        high = rng.randi() & 0xFFFFFFFF

        register = (high << 0x20) | low
        register = ((register >> 33) ^ register) * CONST_A
        register &= 0xFFFFFFFFFFFFFFFF
        register = ((register >> 33) ^ register) * CONST_B
        register &= 0xFFFFFFFFFFFFFFFF
        p_seed = (register >> 33) ^ register
        planet_seeds.append(p_seed)
        i += 1

    # Extra planet
    rng._updateSeed()
    # print(i, n_planets, n_prime_planets)
    while i < (
        system_attributes["planet_count"] + system_attributes["prime_planet_count"]
    ):
        low = rng.randi() & 0xFFFFFFFF
        high = rng.randi() & 0xFFFFFFFF
        size = rng.random(3)
        register = (high << 0x20) | low
        register = ((register >> 33) ^ register) * CONST_A
        register &= 0xFFFFFFFFFFFFFFFF
        register = ((register >> 33) ^ register) * CONST_B
        register &= 0xFFFFFFFFFFFFFFFF
        p_seed = (register >> 33) ^ register
        planet_seeds.append(p_seed)
        i += 1
        if size == 0:  # MassiveSolarSystems is true.
            # This is a large planet
            # Add 1 or 2 moons.
            m = system_attributes["planet_count"] - i
            if m < 0:
                m = 0
            if m > 2:
                m = 2

            n_moons = rng.random(m + 1)
            # print("moons", n_moons)
            if n_moons > 0:
                # rcx_25 = &lOutput_1->maiPlanetParentIndices.maArray[planet_count];
                while i != system_attributes["safe_start_planet"] - 1:
                    # print(3)
                    i += 1
                    # set index to i_2
                    planet_count += 1  # add one to count
                    n_moons -= 1
                    if n_moons <= 0:
                        break

    # print(list(map(lambda x: hex(x), planet_seeds)))
    return planet_seeds[planet_id - 1]


def format_longcode(longcode, digit, alpha):
    return f"{longcode}/{bytes([alpha]).decode('ascii')}{digit}"


def format_shortcode(alpha, num):
    # Shortcodes do not quite work yet. Cant work out where the numeral comes from.
    return f"{bytes([alpha]).decode('ascii')}{num}"


# Returns a planet name given a planet seed.
def planetName(planet_seed_or_code, galaxy=None):
    planet_seed = planet_seed_or_code
    if galaxy is not None:
        planet_seed = planetSeed(planet_seed_or_code, galaxy)

    lowword = planet_seed & 0xFFFFFFFF
    highword = planet_seed >> 32

    rol16 = ((lowword & 0x0000FFFF) << 16) | ((lowword & 0xFFFF0000) >> 16)
    rol16 = (rol16 ^ lowword ^ highword) & 0xFFFFFFFF

    seed = 0
    if lowword == 0:
        seed = ((lowword + 1) * PRNG.MULTIPLIER) + rol16
    else:
        seed = (lowword * PRNG.MULTIPLIER) + rol16

    rng = PRNG(seed)
    adornment = ((rng.seed & 0xFFFFFFFF) * 10) >> 0x20
    # print(f"adornment: {hex(adornment)}")
    code = rng.random(50) + 1
    shortcode = rng.random(0x1A) + 0x41
    # print(f"shortcode: ", bytes([shortcode]).decode("ascii"), hex(shortcode))
    numeral = rng.random(0x12) + 2
    # print(f"numeral: {hex(numeral)}")
    digit = rng.random(0x09) + 1
    # print(f"digit: {hex(digit)}")
    alpha = rng.random(0x1A) + 0x41
    # print(f"alpha: {bytes([alpha]).decode("ascii")} {alpha}")
    longcode = rng.random(0x59) + 0xB
    # print(f"longcode: {hex(longcode)} {longcode}")

    procnorm = generateName(rng, 7, 4, 8)
    procshort = generateName(rng, 5, 4, 5)
    proclong = generateName(rng, 7, 6, 10)
    # print(procnorm, procshort, proclong)

    namegen_style = rng.random(9)
    # print(f"namegen Style: {hex(namegen_style)} {styles[namegen_style]}")

    target = np.double(rng.randi()) * TINY_DOUBLE
    if not (np.double(0.0350000001) <= target):
        # print("TARGET > 0.035")
        namegen_style = 10
        # Do something?

    name = styles[namegen_style]

    name = name.replace("%PROCNORM%", procnorm.capitalize())
    name = name.replace("%PROCSHORT%", procshort.capitalize())
    name = name.replace("%PROCLONG%", proclong.capitalize())
    name = name.replace("%ADORNMENT%", adornments[adornment])
    name = name.replace("%SHORTCODE%", format_shortcode(shortcode, code % 0x50))
    name = name.replace("%NUMERAL%", roman.toRoman(numeral))
    name = name.replace("%LONGCODE%", format_longcode(longcode, digit, alpha))
    # print(name)
    # print("========================================\n\n")
    return name
