from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
import math

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
CONST_B = 0xE36AA5C613612997  # -0x1c955a39ec9ed669


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
#   grf: PSSSGGYYZZZXXX


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


def voxelAttributes(portal_code):
    voxelAttributes = {}
    x = portal_code & 0xFFF
    y = (portal_code & 0xFF000000) >> 24
    z = (portal_code & 0xFFF000) >> 12
    # x/z run 12 bits (0x000-0xFFF), y runs 8 bits (0x00-0xFF): both are
    # signed offsets from the galactic centre, folded the same way the
    # game does (0.00% median error vs 5531 labelled regions). Using the
    # raw unsigned value here instead of folding it made every high-half
    # coordinate look "far",
    # which pushed guide_star_renegade_count to 0 and silently skipped the
    # star_type renegade override for those systems.
    if x > 0x7FF:
        x -= 0x1000
    if z > 0x7FF:
        z -= 0x1000
    if y > 0x7F:
        y -= 0x100
    voxelAttributes["guide_star_count"] = 0x78
    voxelAttributes["black_hole_count"] = 1
    voxelAttributes["atlas_station_count"] = 1
    voxelAttributes["inside_gap"] = 0
    voxelAttributes["guide_star_renegade_count"] = 0

    # The distance is truncated to an integer BEFORE both the gap test and
    # the renegade subtraction, and the subtraction is itself an integer
    # division. Keeping the float distance here rounded a slice of voxels
    # into the wrong band, which shifted guide_star_renegade_count and, with
    # it, the safe-start draw. This one is a fidelity fix, not a scoring
    # one: it moves nothing at all on records discovered in 2025 or later
    # (1,041 purple and 7,314 Euclid systems, identical either way). It only
    # shows up against pre-Origins records, which describe a universe the
    # game no longer generates, so that apparent gain is not evidence.
    distance = int(math.sqrt(x * x + y * y + z * z))
    if distance < 8:
        voxelAttributes["guide_star_count"] = 0
        voxelAttributes["black_hole_count"] = 0
        voxelAttributes["atlas_station_count"] = 0
        voxelAttributes["inside_gap"] = 1

    if 8 < distance < 1440:
        diff = int((distance - 8) * 120 / 1440)

        if diff < 0:
            diff = 0
        if diff > 0x78:
            diff = 0x78
        voxelAttributes["guide_star_renegade_count"] = 0x78 - diff

    return voxelAttributes
