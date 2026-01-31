import unittest
from nms_namegen.system import systemAttributes


class TestSystemAttributes(unittest.TestCase):
    def test_system_attributes_1(self):
        system_attributes = systemAttributes(0x001FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Low",
                "name": "Ancest-Yadn",
                "pirate": False,
                "planet_count": 3,
                "prime_planet_count": 1,
                "race": "Gek",
                "safe_start_planet": 1,
                "star_type": "Yellow",
                "trade_class": "Scientific",
                "wealth": 0,
            },
        )

    def test_system_attributes_2(self):
        system_attributes = systemAttributes(0x002FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "High",
                "name": "Itbyopar",
                "pirate": False,
                "planet_count": 3,
                "prime_planet_count": 2,
                "race": "Korvax",
                "safe_start_planet": 1,
                "star_type": "Yellow",
                "trade_class": "Power Generation",
                "wealth": 1,
            },
        )

    def test_system_attributes_3(self):
        system_attributes = systemAttributes(0x003FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Default",
                "name": "Xohille",
                "pirate": False,
                "planet_count": 6,
                "prime_planet_count": 0,
                "race": "Vy'keen",
                "safe_start_planet": 5,
                "star_type": "Yellow",
                "trade_class": "Technology",
                "wealth": 0,
            },
        )

    def test_system_attributes_4(self):
        system_attributes = systemAttributes(0x004FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Low",
                "name": "Harlando XII",
                "pirate": False,
                "planet_count": 4,
                "prime_planet_count": 2,
                "race": "Vy'keen",
                "safe_start_planet": 2,
                "star_type": "Yellow",
                "trade_class": "Technology",
                "wealth": 1,
            },
        )

    def test_system_attributes_5(self):
        system_attributes = systemAttributes(0x005FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Default",
                "name": "Toseycia",
                "pirate": False,
                "planet_count": 4,
                "prime_planet_count": 1,
                "race": "Gek",
                "safe_start_planet": 3,
                "star_type": "Yellow",
                "trade_class": "Manufacturing",
                "wealth": 1,
            },
        )

    def test_system_attributes_6(self):
        system_attributes = systemAttributes(0x218FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Low",
                "name": "Ritoni",
                "pirate": False,
                "planet_count": 1,
                "prime_planet_count": 1,
                "race": "Gek",
                "safe_start_planet": 2,
                "star_type": "Yellow",
                "trade_class": "Trading",
                "wealth": 2,
            },
        )

    def test_system_attributes_7(self):
        system_attributes = systemAttributes(0x009FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Low",
                "name": "Ineilad",
                "pirate": False,
                "planet_count": 4,
                "prime_planet_count": 1,
                "race": "Gek",
                "safe_start_planet": 2,
                "star_type": "Yellow",
                "trade_class": "Trading",
                "wealth": 1,
            },
        )

    def test_system_attributes_8(self):
        system_attributes = systemAttributes(0x15EFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "Default",
                "name": "Gamumu XIX",
                "pirate": False,
                "planet_count": 2,
                "prime_planet_count": 1,
                "race": "Vy'keen",
                "safe_start_planet": 2,
                "star_type": "Yellow",
                "trade_class": "Technology",
                "wealth": 2,
            },
        )

    def test_system_attributes_empty(self):
        self.maxDiff = None
        system_attributes = systemAttributes(0x1ACFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "abandoned": False,
                "conflict_level": "None",
                "name": "Ucsonvill",
                "pirate": False,
                "planet_count": 5,
                "prime_planet_count": 1,
                "race": "None",
                "safe_start_planet": 0,
                "star_type": "Red",
                "trade_class": "None",
                "wealth": 0,
            },
        )
