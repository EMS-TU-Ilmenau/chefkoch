# -*- coding: utf-8 -*-
# This file holds unit tests for all functions inside the chefkoch module to
# ease the development process.
# Execute this file by typing into a linux console in same directory:
# python -m unittest test_chefkoch
# (maybe test_chefkoch.py depending on linux version) 

import unittest
import chefkoch

class TestChefkoch(unittest.TestCase):

    def test_readjson(self):
        result = chefkoch.readjson("recipe.json")
#        self.assertTrue(isinstance(result, chefkoch.Recipe)) todo fix this line
        self.assertEqual(result.nodes[1].name, "prisma_volume")

