from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
from nms_namegen.iprng import indexPrimedPRNG
from nms_namegen.region import voxelAttributes
import roman
import numpy as np

TINY_DOUBLE = np.double(2.3283064370807974e-10)

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
            n == 19

        name = f"{name} {roman.toRoman(n)}"
    return name


# Returns a dictionary containing system attributes.
def systemAttributes(portal_code, galaxy):
    portal_code = portal_code & 0xFFFFFFFFFFF
    system_id = (portal_code & 0xFFF00000000) >> 32
    universalAddress = (((system_id << 8) | (galaxy & 0xFF)) << 32) | (
        portal_code & 0xFFFFFFFF
    )
    # print("UA:", hex(universalAddress))
    va = voxelAttributes(portal_code)
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

    if system_id < va["guide_star_count"]:
        planet_count = (((seed & 0xFFFFFFFF) * 4) >> 0x20) + 3
        safe_start = rng.random(planet_count) + 1
    else:
        star_type = 0

        if (((seed & 0xFFFFFFFF) * 0x64) >> 0x20) < 0x1E:
            star_type = rng.random(3) + 1

        planet_count = rng.random(6) + 1

        if va["guide_star_renegade_count"] >= 10 or star_type != 0:
            safe_start = 0
        else:
            safe_start = rng.random(planet_count + 2)

    rng._updateSeed()
    rng._updateSeed()
    rng._updateSeed()
    rng._updateSeed()
   
    if (
        system_id < va["guide_star_renegade_count"]
    ):  
        star_type = rng.random(3) + 1

    if system_id > 0x3E9 and system_id < 0x429:  # Purple
        star_type = 4

    rng._updateSeed()
    rng._updateSeed()

    diff = 6 - planet_count
    if diff < 1:
        prime_planet_count = 0
    elif (rng.random(100) >= 33) or diff < 2:
        prime_planet_count = 1

    # unknown_attribute = 0
    unknown_attribute2 = 0
    if star_type == 4:
        planet_count = 0

        if rng.random(100) > 0xF:
            # unknown_attribute = 1
            if rng.random(100) < 0x42 or unknown_attribute2:
                unknown_attribute2 = 1

    if unknown_attribute2:
        planet_count = 0
        star_type = 4
        prime_planet_count = 6

    return {
        "planet_count": planet_count,
        "prime_planet_count": prime_planet_count,
        "safe_start_planet": safe_start
    }
