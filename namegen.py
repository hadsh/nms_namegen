#!/usr/bin/env python3

import sys
import argparse

from nms_namegen.system import systemName
from nms_namegen.region import regionName
from nms_namegen.planet import planetName


def main():
    parser = argparse.ArgumentParser(
        prog="namegen.py",
        description="Generates names for regions, systems and planets in the game No Man's Sky.",
        epilog="",
    )

    parser.add_argument(
        "command",
        choices=["region", "system", "planet"],
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
    sys.exit(0)


if __name__ == "__main__":
    main()
