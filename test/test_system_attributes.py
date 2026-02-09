import unittest
from nms_namegen.system import systemAttributes


class TestSystemAttributes(unittest.TestCase):
    def test_system_attributes_1(self):
        system_attributes = systemAttributes(0x001FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 3,
                "prime_planet_count": 1,
                "safe_start_planet": 1,
            },
        )

    def test_system_attributes_2(self):
        system_attributes = systemAttributes(0x002FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 3,
                "prime_planet_count": 2,
                "safe_start_planet": 1,
            },
        )

    def test_system_attributes_3(self):
        system_attributes = systemAttributes(0x003FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 6,
                "prime_planet_count": 0,
                "safe_start_planet": 5,
            },
        )

    def test_system_attributes_4(self):
        system_attributes = systemAttributes(0x004FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 4,
                "prime_planet_count": 2,
                "safe_start_planet": 2,
            },
        )

    def test_system_attributes_5(self):
        system_attributes = systemAttributes(0x005FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 4,
                "prime_planet_count": 1,
                "safe_start_planet": 3,
            },
        )

    def test_system_attributes_6(self):
        system_attributes = systemAttributes(0x218FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 1,
                "prime_planet_count": 1,
                "safe_start_planet": 2,
            },
        )

    def test_system_attributes_7(self):
        system_attributes = systemAttributes(0x009FF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 4,
                "prime_planet_count": 1,
                "safe_start_planet": 2,
            },
        )

    def test_system_attributes_8(self):
        system_attributes = systemAttributes(0x15EFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 2,
                "prime_planet_count": 1,
                "safe_start_planet": 2,
            },
        )

    def test_system_attributes_empty(self):
        self.maxDiff = None
        system_attributes = systemAttributes(0x1ACFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 5,
                "prime_planet_count": 1,
                "safe_start_planet": 0,
            },
        )
    def test_system_attributes_empty(self):
        self.maxDiff = None
        system_attributes = systemAttributes(0x1ACFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 5,
                "prime_planet_count": 1,
                "safe_start_planet": 0,
            },
        )
        
    def test_system_attributes_blue(self):
        self.maxDiff = None
        system_attributes = systemAttributes(0x51BCFF285671, 9)
        self.assertDictEqual(
            system_attributes,
            {
                "planet_count": 3,
                "prime_planet_count": 2,
                "safe_start_planet": 0,
            },
        )
