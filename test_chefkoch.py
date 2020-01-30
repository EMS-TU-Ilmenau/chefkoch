# -*- coding: utf-8 -*-
# This file holds unit tests for all functions inside the chefkoch module to
# ease the development process.
# Execute this file by typing into a linux console in same directory:
# python -m unittest test_chefkoch
# (maybe test_chefkoch.py depending on python and linux version) 

import unittest
import chefkoch

class TestChefkoch(unittest.TestCase):

    def test_openjson(self):
        # test 1: valid JSON file.
        result, err = chefkoch.openjson("/mnt/c/Users/User/Documents/Hiwi@EMS/chefkoch/recipe.json")
        self.assertTrue(isinstance(result, dict)) 
        self.assertIs(err, None)
        self.assertEqual(result['nodes'][1]['name'], "prisma_volume")

        # test 2: broken JSON file.
        result, err = chefkoch.openjson("/mnt/c/Users/User/Documents/Hiwi@EMS/chefkoch/broken_for_testcase.json")
        self.assertEquals(err, "This is no valid JSON file. Try deleting comments.")
        self.assertIs(result, None)

        # test 3: file path wrong/ file does not exist
        result, err = chefkoch.openjson("NoFileHere.json")
        self.assertEquals(err, "The file path or file name is incorrect.")
        self.assertIs(result, None)

    def test_jsonToRecipe(self):
        # test 1: Not giving a dict as input to jsonToRecipe
        result, err = chefkoch.jsonToRecipe(None)
        self.assertIs(result, None)
        self.assertEqual(err, 'Function jsonToRecipe expects dictionary as input.')

        # test 2: correct format with additional information still works
        data = {
            "nodes": [{
                "name": "rectangle_area",
                "inputs": {"d": "flavour.d", "b": "flavour.b"},
                "unneccessary": "and of no interest",
                "outputs": {"a": "area"},
                "stepsource": "rectangle_area.py"
                }]
            }
        result, err = chefkoch.jsonToRecipe(data)
        self.assertIsInstance(result, chefkoch.Recipe)
        self.assertIsNone(err)
        self.assertEquals(result.nodes[0].inputs['b'], "flavour.b")

        # test 3: incorrect format
        data = {
            "nodes": [{
                "name": "rectangle_area",
                "missing": {},
                "outputs": {"a": "area"},
                "stepsource": "rectangle_area.py"
                }]
            }
        result, err = chefkoch.jsonToRecipe(data)
        self.assertIsNone(result)
        self.assertEquals(err,'An error occured.')

        # test 4: Annoying the Node class
        data = {
            "nodes": [{
                "name": "fancy",
                "inputs": "no dict",
                "outputs": {"a": "area"},
                "stepsource": "no_build-in_function"
                }]
            }
        result, err = chefkoch.jsonToRecipe(data)
        self.assertIsNone(result)
        self.assertIsNotNone(err)

        # todo: data versions in object with expected result and err value and loop!




