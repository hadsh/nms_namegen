from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
import roman

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

    # Swap words
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

    cache1 = 0x000600

    # Sets the alphaset index (low byte of cache1)
    alphaset_reg = ((seed & 0xFFFFFFFF) * 0x5) >> 32
    if alphaset_reg == 0:
        cache1 |= 0x02
    else:
        if (alphaset_reg & 0xFF) < 0x04:
            cache1 |= (alphaset_reg & 0xFF) + 0x02
        else:
            cache1 |= 0x07

    # Set high byte of cache1
    cache1 = ((rng.random(4) + 0x06) << 16) | cache1

    name, w = generateName(rng, cache1)
    name = name.capitalize()

    # Hyphenated names
    if len(name) < 8:
        r = rng.random(4)
        if r < 2:
            cache1 = 0x000300
            cache1 |= (r + 5) << 16
            alphaset_reg = rng.random(5)
            if alphaset_reg == 0:
                cache1 |= 0x02
            else:
                if alphaset_reg < 4:
                    cache1 |= alphaset_reg + 2
                else:
                    cache1 |= 0x07

            name2, cache1 = generateName(rng, cache1)
            name = f"{name}-{name2.capitalize()}"

    # Might have to tune the rng parameter here.
    # I'm not sure where the cutoff actually as yet
    if rng.random(0x0A) < 0x03:
        n = (rng.random(19)) + 1
        if n > 19:
            n == 19

        name = f"{name} {roman.toRoman(n)}"
    return name
