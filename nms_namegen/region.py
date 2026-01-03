from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG

region_name_adornments = [
    "{} Adjunct",
    "{} Void",
    "{} Expanse",
    "{} Terminus",
    "{} Boundary",
    "{} Fringe",
    "{} Cluster",
    "{} Mass",
    "{} Band",
    "{} Cloud",
    "{} Nebula",
    "{} Quadrant",
    "{} Sector",
    "{} Anomaly",
    "{} Conflux",
    "{} Instability",
    "Sea of {}",
    "The Arm of {}",
    "{} Spur",
    "{} Shallows",
]
CONST_A = 0x64DD81482CBD31D7
CONST_B = 0xE36AA5C613612997


# Returns a region name for No Man's Sky
#
# Parameters:
#   Portal code as a hexadecimal integer,
#   in the format 0xPSSSYYZZZXXX
#   Where P - Planet id (unused)
#   SSS - System Id (unused)
#   YY - Y coordinate
#   ZZZ - Z coordinate
#   XXX - X coordinate
#
#   Galaxy is the galaxy number starting with Euclid as 0.
#   
def regionName(portal_code, galaxy):
    register = galaxy >> 1
    register ^= (galaxy << 32) | (portal_code & 0xFFFFFFFF)
    register = register * CONST_A
    register &= 0xFFFFFFFFFFFFFFFF
    register = ((register >> 33) ^ register) * CONST_B
    register &= 0xFFFFFFFFFFFFFFFF
    register = (register >> 33) ^ register

    seed_h = (
        (((register & 0xFFFF0000) >> 16) | ((register & 0x0000FFFF) << 16))
        ^ (register & 0xFFFFFFFF)
        ^ (register >> 32)
    )
    seed = register & 0xFFFFFFFF
    if seed_h == 0:
        seed_h = 1

    seed |= seed_h << 32
    rng = PRNG(seed)

    min_length = 6
    max_length = rng.random(4) + 6
    alphaset_index = 0
    name = generateName(rng, alphaset_index, min_length, max_length)
    name = name.capitalize()

    if rng.random(0x64) < 0x50:
        adornment = region_name_adornments[rng.random(0x14)]
        name = adornment.format(name)

    return name
