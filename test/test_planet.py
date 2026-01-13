import unittest
from nms_namegen.planet import planetName, planetSeed

import json


class TestPlanet(unittest.TestCase):
    # WIP
    # def test_planet_seed(self):
    #     planet_seed = 0x770122D46A4D41B8
    #     seed = planetSeed(0x21FBFF285671, 9)
    #     print(hex(seed))
    #     self.assertEqual(hex(seed), hex(planet_seed))

    def test_planet_name(self):
        planet_seed = 0x6AC66FF304FA712A # Risidosiu X
        self.assertEqual(planetName(planet_seed), "Risidosiu X")    
    
    def test_planet_name_2(self):
        planet_seed = 0x5AFEFB83E5EE3F6F
        self.assertEqual(planetName(planet_seed), "Nobern")
     
    def test_planet_name_3(self):
        planet_seed = 0x770122D46A4D41B8
        self.assertEqual(planetName(planet_seed), "Thyonica Rioka")

    def test_planet_name_4(self):
        planet_seed = 0xC34A0DC905122C61
        self.assertEqual(planetName(planet_seed), "Mopos")

    def test_planet_name_5(self):
        planet_seed = 0x85F5F46C72CBB84
        self.assertEqual(planetName(planet_seed), "Oulder VI")

    def test_planet_name_6(self):
        planet_seed = 0x1079D1B212B1D8C4
        self.assertEqual(planetName(planet_seed), "Onnett V")
   
    def test_planet_name_7(self):
        planet_seed = 0x24755ED15910B159
        self.assertEqual(planetName(planet_seed), "Liyoneh Minor")

    def test_planet_name_8(self):
        planet_seed = 0xCC997F1AE2B093A6
        self.assertEqual(planetName(planet_seed), "New Retcolyn")

    def test_planet_names(self):
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
        ]
        errors = []
        for i in (seeds):
            name = planetName(i[0])
            if(name != i[1]):
                errors.append((i[1], name))

        self.assertEqual([], errors)
