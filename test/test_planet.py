import unittest
from nms_namegen.planet import planetName, planetSeed


class TestPlanet(unittest.TestCase):
    # # WIP
    def test_planet_seed(self):
        #     # Gamumu system
        planet_seed = 0x6087656AFFF5A7CF
        seed = planetSeed(0x115EFF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xB65706582461C369
        seed = planetSeed(0x215EFF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0x88D131C14DF00E25
        seed = planetSeed(0x315EFF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

    def test_planet_seed_2(self):
        # Sefielde system
        planet_seed = 0x5777F1C8A290BDF4
        seed = planetSeed(0x1094FF4185BA, 0)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xAF013A23FEE67C33
        seed = planetSeed(0x2094FF4185BA, 0)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xA70E3A6BA5AF2A0
        seed = planetSeed(0x3094FF4185BA, 0)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0x75879E53D547CC8F
        seed = planetSeed(0x4094FF4185BA, 0)
        self.assertEqual(hex(seed), hex(planet_seed))

    def test_planet_seed_3(self):
        # Xohille system 3 planets 3 moons
        planet_seed = 0xF9DAFFE75B87C65
        seed = planetSeed(0x1003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0x39222BFD8DEDE48A
        seed = planetSeed(0x2003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xC532445CDBDA396F
        seed = planetSeed(0x3003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0x9EBB56AF9E5A62BA
        seed = planetSeed(0x4003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xE5A5CD32465CA2B9
        seed = planetSeed(0x5003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

        planet_seed = 0xC961CCCD7395E843
        seed = planetSeed(0x6003FF285671, 9)
        self.assertEqual(hex(seed), hex(planet_seed))

    def test_planet_name_from_seed(self):
        planet_seed = 0x6AC66FF304FA712A
        self.assertEqual(planetName(planet_seed), "Risidosiu X")

    def test_planet_name_from_seed_2(self):
        planet_seed = 0x5AFEFB83E5EE3F6F
        self.assertEqual(planetName(planet_seed), "Nobern")

    def test_planet_name_from_seed_3(self):
        planet_seed = 0x770122D46A4D41B8
        self.assertEqual(planetName(planet_seed), "Thyonica Rioka")

    def test_planet_name_from_seed_4(self):
        planet_seed = 0xC34A0DC905122C61
        self.assertEqual(planetName(planet_seed), "Mopos")

    def test_planet_name_from_seed_5(self):
        planet_seed = 0x85F5F46C72CBB84
        self.assertEqual(planetName(planet_seed), "Oulder VI")

    def test_planet_name_from_seed_6(self):
        planet_seed = 0x1079D1B212B1D8C4
        self.assertEqual(planetName(planet_seed), "Onnett V")

    def test_planet_name_from_seed_7(self):
        planet_seed = 0x24755ED15910B159
        self.assertEqual(planetName(planet_seed), "Liyoneh Minor")

    def test_planet_name_from_seed_8(self):
        planet_seed = 0xCC997F1AE2B093A6
        self.assertEqual(planetName(planet_seed), "New Retcolyn")

    def test_planet_names_from_seeds(self):
        seeds = [
            [0xD3C191A9D28534E9, "Iacre V"],
            [0x42479ECA7A3B9205, "Kotos 34/G8"],
            [0xD8AE4871B9EEF06D, "Kuki 23/D1"],
            [0x71DA29B088E68D53, "Roton XIX"],
            [0xF9C70249A94306ED, "Wobur IV"],
            [0xC871D1C804AE93EB, "Diadusis H29"],
            [0x1219707B3711D500, "Lathes K28"],
            [0x9E6038BFFE8D797B, "Mazu 39/G7"],
            [0x578CC780BAEB5C94, "Akotap XIX"],
            [0xB9FED597B2582A45, "Ophi X36"],
            [0x6F89A5F3C13E2F20, "Ristonor XIX"],
            [0x24755ED15910B159, "Liyoneh Minor"],
            [0xF9DAFFE75B87C65, "Bedalmbe Tau"],
            [0x793279A766FE33B2, "Equu Alpha"],
            [0xD77E5E787AC1D333, "Yuningo Tau"],
            [0x39222BFD8DEDE48A, "Hioscarpa Fujin"],
            [0xC532445CDBDA396F, "New Ikasma"],
            [0x9EBB56AF9E5A62BA, "Fuefu 84/X5"],
            [0xE5A5CD32465CA2B9, "Liltons Toba"],
            [0xC961CCCD7395E843, "Enbrigan"],
            [0x6087656AFFF5A7CF, "Nafra"],
            [0xB65706582461C369, "Arva Y35"],
            [0x88D131C14DF00E25, "Stagitti V"],
            [0x8B79B3708BB3EBEC, "Elagatal Beta"],
            [0x16E230F95F23DCF9, "Eesap U41"],
            [0xC54DCA751F0F23EF, "Pearlo Omega"],
        ]

        errors = []
        for i in seeds:
            name = planetName(i[0])
            if name != i[1]:
                errors.append((i[1], name))

        self.assertEqual([], errors)

    def test_planet_name_from_portal_code(self):
        name = planetName(0x115EFF285671, 9)
        self.assertEqual(name, "Nafra")
        name = planetName(0x215EFF285671, 9)
        self.assertEqual(name, "Arva Y35")

    def test_planet_name_from_portal_code_2(self):
        # name = planetName(0x1001FF285671, 9, 2)
        seed = planetSeed(0x1001FF285671, 9)
        name = planetName(seed)
        self.assertEqual(name, "Lewaukee Megu")
