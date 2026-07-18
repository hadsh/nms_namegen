import json
import subprocess
import sys
import unittest

from namegen import systemComposition


class TestSystemComposition(unittest.TestCase):
    def test_composition_dict(self):
        # Alsvol-Bushi X (portal 003df8f87945, Euclid): a non-gas-giant
        # system with three planets and a single moon.
        composition = systemComposition(0x003DF8F87945, 0)
        self.assertEqual(
            composition,
            {
                "planet_count": 3,
                "prime_planet_count": 1,
                "safe_start_planet": 3,
                "gas_giant": False,
                "star_type": 0,
                "rendered_planets": 3,
                "rendered_moons": 1,
            },
        )

    def test_non_gas_giant_rendered_split_totals(self):
        # For non-gas-giant systems the rendered planet/moon split accounts for
        # every body the seed generator placed (planet_count + prime_planet_count).
        # This invariant does NOT hold for gas giants (see the gas-giant test).
        for portal_code in [0x001FF285671, 0x003FF285671, 0x218FF285671]:
            composition = systemComposition(portal_code, 9)
            self.assertFalse(composition["gas_giant"])
            self.assertEqual(
                composition["rendered_planets"] + composition["rendered_moons"],
                composition["planet_count"] + composition["prime_planet_count"],
            )

    def test_gas_giant_rendered_split_is_fixed(self):
        # planetSeeds overrides gas-giant systems to a fixed 1 planet + 5 moons
        # regardless of the logical planet_count, so the rendered split
        # deliberately diverges from planet_count + prime_planet_count.
        composition = systemComposition(0x03E912345678, 0)
        self.assertTrue(composition["gas_giant"])
        self.assertEqual(composition["rendered_planets"], 1)
        self.assertEqual(composition["rendered_moons"], 5)


class TestAttributesCLI(unittest.TestCase):
    def test_attributes_command_outputs_json(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "attributes", "-p", "003df8f87945", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "planet_count": 3,
                "prime_planet_count": 1,
                "safe_start_planet": 3,
                "gas_giant": False,
                "star_type": 0,
                "rendered_planets": 3,
                "rendered_moons": 1,
            },
        )

    def test_attributes_command_requires_portal_code(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "attributes", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("portal code", result.stderr + result.stdout)


class TestSystemAttributesCLI(unittest.TestCase):
    def test_system_attributes_command_outputs_json(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "system-attributes", "-p", "003df8f87945", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "planet_count": 3,
                "prime_planet_count": 1,
                "safe_start_planet": 3,
                "gas_giant": False,
                "star_type": 0,
            },
        )

    def test_system_attributes_command_requires_portal_code(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "system-attributes", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("portal code", result.stderr + result.stdout)


class TestPlanetSeedsCLI(unittest.TestCase):
    def test_planet_seeds_command_outputs_json(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "planet-seeds", "-p", "003df8f87945", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "planet_seeds": [
                    6957366409789192041,
                    11872164497817189863,
                    12193988597400712801,
                    6531008701629202253,
                ],
                "planet_count": 3,
                "moon_count": 1,
            },
        )

    def test_planet_seeds_command_requires_portal_code(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "planet-seeds", "-g", "0"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("portal code", result.stderr + result.stdout)


class TestVoxelCLI(unittest.TestCase):
    def test_voxel_command_outputs_json(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "voxel", "-p", "003df8f87945"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "guide_star_count": 120,
                "black_hole_count": 1,
                "atlas_station_count": 1,
                "inside_gap": 0,
                "guide_star_renegade_count": 0,
            },
        )

    def test_voxel_command_requires_portal_code(self):
        result = subprocess.run(
            [sys.executable, "namegen.py", "voxel"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("portal code", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
