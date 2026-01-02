import unittest
from nms_namegen.region import regionName
from nms_namegen.system import systemName
import json


class TestGenerator(unittest.TestCase):
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

    def test_system_names(self):
        roman_codes = [
            [0x01FBFF285671, 9, "Aemilyinn XIX"],
            [0x0004FF285671, 9, "Harlando XII"],
            [0x015EFF285671, 9, "Gamumu XIX"],
            [0x0037008F8FE3, 9, "Tiundar XIX"],
            [0x0064FF285671, 9, "Veparter VIII"],
            [0x01ECFF285671, 9, "Aylerai XIII"],
        ]

        hyphen_codes = [
            [0x0001FF285671, 9, "Ancest-Yadn"],
            [0x01EDFF285671, 9, "Ohamno-Pavl"],
            [0x0007FF285671, 9, "Sachipp-Imhae"],
            [0x01A1FF285671, 9, "Essing-Agur"],
            [0x00420007A906, 0, "Oavslue-Kotyvik"],
            [0x002FDCD6424D, 0, "Aakita-Ebre"],
        ]

        plain_codes = [
            [0x00D9008F8FE3, 9, "Dapunkt"],
            [0x004A008F8FE3, 9, "Setturke"],
            [0x01ACFF285671, 9, "Ucsonvill"],
            [0x01DAFF285671, 9, "Atiere"],
            [0x0002FF285671, 9, "Itbyopar"],
            [0x0003FF285671, 9, "Xohille"],
            [0x0005FF285671, 9, "Toseycia"],
            [0x0006FF285671, 9, "Ephiakar"],
            [0x0218FF285671, 9, "Ritoni"],
        ]

        hyphen_roman_codes = [
            [0x0080008F8FE3, 9, "Rotalo-Romok VIII"],
            [0x014FFF285671, 9, "Mikesm-Remat V"],
            [0x01F8FF285671, 9, "Naheil-Aichi XI"],
        ]

        print("--- plain ---")
        for code in plain_codes:
            name = systemName(code[0], code[1])
            print(f"{name} // {code[1]}")
            self.assertEqual(name, code[2])

        print("--- hyphen ---")
        for code in hyphen_codes:
            name = systemName(code[0], code[1])
            print(f"{name} // {code[1]}")
            self.assertEqual(name, code[2])

        print("--- roman ---")
        for code in roman_codes:
            name = systemName(code[0], code[1])
            print(f"{name} // {code[1]}")
            self.assertEqual(name, code[2])

        print("--- hyphen roman ---")
        for code in hyphen_roman_codes:
            name = systemName(code[0], code[1])
            print(f"{name} // {code[1]}")
            self.assertEqual(name, code[2])
    
    def test_AGT_data(self):
       # This tests against verified data from AGT
        with open("test/fixtures/system_names.json") as file:
            data = json.load(file)
        e = len(data)
        best = ()
        errors = []
        for system in data:
            portal_code = int(system[2], 16)
            system_name = systemName(portal_code, 0)
            if system_name != system[0]:
                errors.append((system_name, system[0], system[2]))
        self.maxDiff = None
        self.assertEqual(errors, [])
