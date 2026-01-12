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
   
 