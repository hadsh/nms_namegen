import json
import unittest

from nms_namegen.region import regionName, voxelAttributes
from nms_namegen.system import systemName, systemAttributes, planetSeeds
from nms_namegen.planet import planetName


# The reference vectors were captured through a 64-bit signed integer type,
# so seeds above 2**63 are stored as negative two's-complement values.
# planetSeeds() here returns them unsigned, so fold both to the same
# unsigned 64-bit range before comparing.
def _u64(n):
    return n & 0xFFFFFFFFFFFFFFFF


# Cross-checked against an independent second implementation of this
# library (region/system/planet names, system attributes, planet seeds
# and voxel attributes), 443 portal codes across a range of galaxies,
# 0 mismatches on any field.
class TestGoldenVectors(unittest.TestCase):
    def test_golden_vectors(self):
        with open("test/fixtures/golden_vectors.json") as file:
            cases = json.load(file)

        errors = []
        for rec in cases:
            code = rec["code"]
            galaxy = rec["galaxy"]
            tag = f"{code}/g{galaxy}"

            region = regionName(code, galaxy)
            if region != rec["region"]:
                errors.append(f"region {tag}: got {region!r}, expected {rec['region']!r}")

            system = systemName(code, galaxy)
            if system != rec["system"]:
                errors.append(f"system {tag}: got {system!r}, expected {rec['system']!r}")

            if not str(rec["planet"]).startswith("ERR:"):
                planet = planetName(code, galaxy)
                if planet != rec["planet"]:
                    errors.append(f"planet {tag}: got {planet!r}, expected {rec['planet']!r}")

            attrs = systemAttributes(code, galaxy)
            expected_attrs = rec["sysattr"]
            if attrs != expected_attrs:
                errors.append(f"sysattr {tag}: got {attrs}, expected {expected_attrs}")

            seeds = planetSeeds(code, galaxy)
            expected_seeds = [_u64(s) for s in rec["seeds"]]
            if (
                [_u64(s) for s in seeds["planet_seeds"]] != expected_seeds
                or seeds["planet_count"] != rec["planet_count"]
                or seeds["moon_count"] != rec["moon_count"]
                or seeds["sizes"] != rec["sizes"]
            ):
                errors.append(
                    f"seeds {tag}: got planet_count={seeds['planet_count']} "
                    f"moon_count={seeds['moon_count']} sizes={seeds['sizes']}, "
                    f"expected planet_count={rec['planet_count']} "
                    f"moon_count={rec['moon_count']} sizes={rec['sizes']}"
                )

            voxel = voxelAttributes(code)
            expected_voxel = rec["voxel"]
            voxel_ok = (
                voxel["guide_star_count"] == expected_voxel["guide_star_count"]
                and voxel["black_hole_count"] == expected_voxel["black_hole_count"]
                and voxel["atlas_station_count"] == expected_voxel["atlas_station_count"]
                and voxel["inside_gap"] == expected_voxel["inside_gap"]
                and abs(
                    float(voxel["guide_star_renegade_count"])
                    - float(expected_voxel["guide_star_renegade_count"])
                )
                < 1e-9
            )
            if not voxel_ok:
                errors.append(f"voxel {tag}: got {voxel}, expected {expected_voxel}")

        if errors:
            self.fail(f"{len(errors)} mismatch(es):\n" + "\n".join(errors[:20]))


if __name__ == "__main__":
    unittest.main()
