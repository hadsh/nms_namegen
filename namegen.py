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
#     those bodies are actually split into planets vs moons. Every moon takes
#     one of the logical body slots, so rendered_planets + rendered_moons
#     equals planet_count + prime_planet_count but rendered_planets alone
#     deliberately does not.
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


# Reads portal codes from stdin and writes one JSON object per line to stdout.
#
# Every other command pays the interpreter and numpy import cost per address,
# which is fine for a single lookup but dominates completely when a caller wants
# to sift thousands of addresses looking for ones with particular attributes.
# Amortising that startup over the whole run is the entire point: the work per
# address is microseconds, the startup is not.
#
# Input:  one address per line, optionally "<address> <galaxy>" (galaxy defaults
#         to the -g value). Blank lines and lines starting with # are skipped.
# Output: one JSON object per line, in input order, each carrying the address and
#         galaxy it describes so a caller can stream without tracking position.
#         A bad line yields {"address": ..., "error": ...} rather than aborting
#         the run -- a caller sifting random addresses expects some to be junk.
#
# The stream is flushed per line so a caller can consume results as they arrive
# rather than waiting for the process to exit.
def runBatch(stream, default_galaxy, what):
    for raw in stream:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        address = parts[0]
        galaxy = default_galaxy
        if len(parts) > 1:
            try:
                galaxy = int(parts[1])
            except ValueError:
                print(json.dumps({"address": address,
                                  "error": "invalid galaxy"}), flush=True)
                continue
        try:
            code = int(address, 16)
            if len(address) != 12:
                raise ValueError("portal code must be 12 hex digits")
            if galaxy < 0 or galaxy > 255:
                raise ValueError("galaxy must be in range 0-255")
        except ValueError as exc:
            print(json.dumps({"address": address, "error": str(exc)}), flush=True)
            continue

        try:
            if what == "system-attributes":
                record = systemAttributes(code, galaxy)
            elif what == "attributes":
                record = systemComposition(code, galaxy)
            elif what == "voxel":
                record = voxelAttributes(code)
            elif what == "system":
                record = {"system_name": systemName(code, galaxy)}
            elif what == "region":
                record = {"region_name": regionName(code, galaxy)}
            elif what == "planet":
                record = {"planet_name": planetName(code, galaxy)}
            else:
                record = {"error": "unknown batch kind: %s" % what}
        except Exception as exc:  # one bad address must not end the run
            record = {"error": "%s: %s" % (type(exc).__name__, exc)}
        record["address"] = address
        record["galaxy"] = galaxy
        print(json.dumps(record), flush=True)


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
            "batch",
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
    parser.add_argument(
        "--batch-kind",
        choices=[
            "system-attributes",
            "attributes",
            "voxel",
            "system",
            "region",
            "planet",
        ],
        default="system-attributes",
        help="""
        For the batch command: which record to emit per address.
        Defaults to system-attributes.
""",
    )

    args = parser.parse_args()

    if args.command == "batch":
        runBatch(sys.stdin, args.galaxy, args.batch_kind)
        sys.exit(0)

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
