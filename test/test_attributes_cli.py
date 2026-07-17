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
                "planets": 3,
                "moons": 1,
            },
        )

    def test_composition_planet_moon_totals(self):
        # planets + moons must account for every body the seed generator
        # placed (planet_count + prime_planet_count).
        for portal_code in [0x001FF285671, 0x003FF285671, 0x218FF285671]:
            composition = systemComposition(portal_code, 9)
            self.assertEqual(
                composition["planets"] + composition["moons"],
                composition["planet_count"] + composition["prime_planet_count"],
            )


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
                "planets": 3,
                "moons": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
