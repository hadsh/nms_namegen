from nms_namegen.generator import generateName
from nms_namegen.prng import PRNG
import numpy as np
import roman 

CONST_A = 0x64DD81482CBD31D7
CONST_B = 0xE36AA5C613612997

adornments = [
    "",
    "Prime",
    "Major",
    "Minor",
    "Alpha",
    "Beta",
    "Gamma",
    "Delta",
    "Omega",
    "Sigma",
    "Tau"
]

styles = [
    "%PROCNORM%",
    "%PROCNORM% %ADORNMENT%", 
    "%PROCNORM% %NUMERAL%",
    "%PROCNORM% %SHORTCODE%",
    "%PROCLONG% %PROCSHORT%",
    "%PROCSHORT% %LONGCODE%",
    "New %PROCNORM%",
    "%PROCNORM%",
    "%PROCNORM% %NUMERAL%",
    "Style 9"
]

TINY_DOUBLE = np.double(2.3283064370807974e-10)

# TODO: Is it possible to generate a planet seed from portal_code + galaxy?
# It should be but seems to be very convoluted.
def planetSeed(portal_code, galaxy):
    # This does not work yet.
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
    
    rng = PRNG(seed) # This should be the system seed??
    print(hex(rng.seed))
    
    register = rng.randi() | rng.randi() 
    register = ((register >> 33) ^ register) * CONST_A
    register &= 0xFFFFFFFFFFFFFFFF
    register = ((register >> 33) ^ register) * CONST_B
    register &= 0xFFFFFFFFFFFFFFFF
    register = (register >> 33) ^ register
    return register


# Returns a planet name given a planet seed. 
def planetName(planet_seed):
    lowword = planet_seed & 0xFFFFFFFF
    highword = planet_seed >> 32

    rol16 = ((lowword & 0x0000FFFF) << 16) | (
        (lowword & 0xFFFF0000) >> 16
    )
    rol16 = (rol16 ^ lowword ^ highword) & 0xFFFFFFFF

    seed = 0
    if lowword == 0:
        seed = ((lowword + 1) * PRNG.MULTIPLIER) + rol16
    else:
        seed = (lowword * PRNG.MULTIPLIER) + rol16

    rng = PRNG(seed)

    adornment = rng.random(10) + 1
    print(f"adornment: {hex(adornment)}")
    shortcode = rng.random(0x1a) + 0x41
    print(f"shortcode: {hex(shortcode)}")   
    numeral = rng.random(0x12) + 2
    print(f"numeral: {hex(numeral)}")
    unknown = rng.random(0x09) + 1
    print(f"unknown: {hex(unknown)}")
    rng._updateSeed()
    longcode = rng.random(0x59) + 0xB
    print(f"longcode: {hex(longcode)}")

    procnorm = generateName(rng, 7, 4, 8)
    procshort = generateName(rng, 5, 4, 5)
    proclong = generateName(rng, 7, 6, 10)
    print(procnorm, procshort, proclong)

    namegen_style = rng.random(9)
    print(f"namegen Style: {hex(namegen_style)}") 

    target = rng.randi() * TINY_DOUBLE
    if target > 0.0350000001:
        print("TARGET > 0.035")
        # Do something?

    name = styles[namegen_style]


    print(name)
    name = name.replace("%PROCNORM%", procnorm.capitalize())
    name = name.replace("%PROCSHORT%", procshort.capitalize())
    name = name.replace("%PROCLONG%", proclong.capitalize())
    name = name.replace("%ADORNMENT%", adornments[adornment])
    name = name.replace("%SHORTCODE%", hex(shortcode))
    name = name.replace("%NUMERAL%", roman.toRoman(numeral))
    name = name.replace("%LONGCODE%", hex(longcode))
   
    return name