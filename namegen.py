#!/usr/bin/env python3

import sys
import json
import argparse

from nms_namegen.system import systemName, systemAttributes, planetSeeds
from nms_namegen.region import regionName, voxelAttributes
from nms_namegen.planet import planetName


# Returns the composition attributes of a system as a plain dict, combining
# systemAttributes (planet/prime counts, safe start, gas giant) with the
# planet-vs-moon split derived from planetSeeds.
#
# The two sources use different notions of "planet count", so the keys are
# named to keep them distinct:
#   * planet_count / prime_planet_count come from systemAttributes and describe
#     the logical bodies the game assigns to the system.
#   * rendered_planets / rendered_moons come from planetSeeds and describe how
#     those bodies are actually split into planets vs moons. For gas giants
#     planetSeeds overrides this to 1 planet + 5 moons, so the rendered split
#     deliberately does NOT equal planet_count + prime_planet_count.
def systemComposition(portal_code, galaxy):
    attributes = systemAttributes(portal_code, galaxy)
    seeds = planetSeeds(portal_code, galaxy)
    return {
        "planet_count": attributes["planet_count"],
        "prime_planet_count": attributes["prime_planet_count"],
        "safe_start_planet": attributes["safe_start_planet"],
        "gas_giant": attributes["gas_giant"],
        "star_type": attributes["star_type"],
        "rendered_planets": seeds["planet_count"],
        "rendered_moons": seeds["moon_count"],
    }


def main():
    parser = argparse.ArgumentParser(
        prog="namegen.py",
        description="Generates names for regions, systems and planets in the game No Man's Sky.",
        epilog="",
    )

    parser.add_argument(
        "command",
        choices=[
            "region",
            "system",
            "planet",
            "attributes",
            "system-attributes",
            "planet-seeds",
            "voxel",
        ],
        help="The type of object to get the name of.",
    )

    parser.add_argument(
        "-p",
        "--portal_code",
        metavar="PSSSYYZZZXXX",
        help="""
    The portal code of the region, system or planet. A 12 digit hexadecimal number, format: PSSSYYZZZXXX. For regions the planet and system parts are
    ignored, for systems the planet id is ignored.
""",
        default=None,
    )

    parser.add_argument(
        "-g",
        "--galaxy",
        type=int,
        help="""
        The galaxy id for the object to be named. 
        Must be in the range 0-255.
        Defaults to 0 (Euclid).
""",
        default=0,
    )

    parser.add_argument(
        "-s",
        "--seed",
        help="""
        This is the seed of a planet. Must be a hexidecimal number. It can be found in save game files.
        Using this overrides portal_code and galaxy options. Has no effect for regions or systems.
""",
        default=0,
    )
    args = parser.parse_args()

    if args.portal_code:
        try:
            portal_code = int(args.portal_code, 16)
        except ValueError:
            print("Invalid portal code.")
            sys.exit(2)

    if args.galaxy < 0 or args.galaxy > 255:
        print("Invalid galaxy id. Must be in range 0-255.")
        sys.exit(2)

    if args.seed:
        try:
            seed = int(args.seed, 16)
        except ValueError:
            print("Invalid seed. Must be a hexidecimal number.")

    if args.command == "system":
        print(systemName(portal_code, args.galaxy))
    if args.command == "region":
        print(regionName(portal_code, args.galaxy))
    if args.command == "planet":
        if args.seed:
            print(planetName(seed))
        else:
            print(planetName(portal_code, args.galaxy))
    if args.command == "attributes":
        if not args.portal_code:
            print("A portal code (-p) is required for the attributes command.")
            sys.exit(2)
        print(json.dumps(systemComposition(portal_code, args.galaxy)))
    if args.command == "system-attributes":
        if not args.portal_code:
            print("A portal code (-p) is required for the system-attributes command.")
            sys.exit(2)
        print(json.dumps(systemAttributes(portal_code, args.galaxy)))
    if args.command == "planet-seeds":
        if not args.portal_code:
            print("A portal code (-p) is required for the planet-seeds command.")
            sys.exit(2)
        print(json.dumps(planetSeeds(portal_code, args.galaxy)))
    if args.command == "voxel":
        if not args.portal_code:
            print("A portal code (-p) is required for the voxel command.")
            sys.exit(2)
        print(json.dumps(voxelAttributes(portal_code)))
    sys.exit(0)


if __name__ == "__main__":
    main()
