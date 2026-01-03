import unittest
from nms_namegen.region import regionName
import json


class TestRegion(unittest.TestCase):
    def test_region_name(self):
        portal_code = 0x01FBFF285671
        galaxy = 9
        reg = regionName(portal_code, galaxy)
        self.assertEqual("Jeffriy Instability", reg)

    def test_5000_region_names(self):
        # This tests against randomly generated region names from
        # the SystemNameCalculator C sharp code.
        with open("test/fixtures/region_names.json") as file:
            data = json.load(file)
        errors = []
        for grf in data:
            portal_code = int(grf, 16) & 0xFFFFFFFF
            galaxy = int(grf, 16) >> 32
            region = regionName(portal_code, galaxy)
            if region != data[grf]:
                errors.append((grf, data[grf], region))
        self.maxDiff = 500
        self.assertEqual(errors, [])
