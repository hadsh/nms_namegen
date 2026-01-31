#!/usr/bin/env python3

import sys
from nms_namegen.system import systemName
from nms_namegen.region import regionName
from nms_namegen.planet import planetName


def usage():
    print("Usage:")
    print("\tnms_namegen.py command portal_code galaxy")
    print("")
    print("command - either region or system.")
    print("portal_code must be a string of 12 hexadecimal digits.")
    print("galaxy is the galaxy id. These start from 0 - Euclid up to 255.")
    print("")
    print("\tnms_namegen.py planet planet_code")
    print("")
    print(
        "planet_seed is a hexadecimal number of 16 digits. You can find them in save files."
    )


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        usage()
        sys.exit(0)

    if len(sys.argv) not in [3, 4] and sys.argv[1] == "planet":
        usage()
        sys.exit(0)

    if len(sys.argv) != 4 and sys.argv[1] in ["system", "region"]:
        usage()
        sys.exit(1)

    command = sys.argv[1]

    if command not in ["system", "region", "planet"]:
        print(
            "Command must be either 'system' or 'region' or 'planet'", file=sys.stderr
        )
        sys.exit(2)

    if command in ["system", "region"] and len(sys.argv[2]) != 12:
        print("Portal code must be 12 hexadecimal digits", file=sys.stderr)
        sys.exit(2)

    try:
        portal_code = int(sys.argv[2], 16)
    except ValueError:
        print("Invalid portal code or planet_seed", sys.argv[2], file=sys.stderr)
        sys.exit(2)

    if command in ["system", "region"]:
        try:
            galaxy = int(sys.argv[3])
        except ValueError:
            print("Invalid galaxy id", sys.argv[3], file=sys.stderr)
            sys.exit(2)
        if galaxy < 0 or galaxy > 255:
            print("Galaxy value out of range 0-255", file=sys.stderr)
            sys.exit(2)

    if command == "planet" and len(sys.argv) == 4:
        try:
            galaxy = int(sys.argv[3])
        except ValueError:
            print("Invalid galaxy id", sys.argv[3], file=sys.stderr)
            sys.exit(2)
        if galaxy < 0 or galaxy > 255:
            print("Galaxy value out of range 0-255", file=sys.stderr)
            sys.exit(2)

    if command == "system":
        print(systemName(portal_code, galaxy))
    if command == "region":
        print(regionName(portal_code, galaxy))
    if command == "planet":
        if len(sys.argv) == 3:
            print(planetName(portal_code))
        else:
            print(planetName(portal_code, galaxy))
    sys.exit(0)


if __name__ == "__main__":
    main()
