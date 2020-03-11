# -*- coding: utf-8 -*-
# This file holds unit tests for all functions inside the chefkoch module to
# ease the development process.
# Execute this file by typing into a linux console in same directory:
# python3 -m unittest test_chefkoch
# subtests are only available from python 3.4 on
# (maybe test_chefkoch.py depending on python and linux version)

import os
import unittest
import sys
import chefkoch.recipe as backbone
import chefkoch

# todo: Konsultiere Fabian

class TestChefkoch(unittest.TestCase):

    def test_readjson(self):
        result, err = chefkoch.readjson('recipe', 'recipe.json')
        self.assertIsNone(err)

class TestRecipe(unittest.TestCase):

    def test_openjson(self):
        # test 1: valid JSON recipe file.
        with self.subTest("test 1: Valid JSON recipe file."):
            result, err = backbone.openjson('recipe.json')
            self.assertTrue(isinstance(result, dict))
            self.assertIsNone(err)
            self.assertEqual(result['nodes'][1]['name'], "prisma_volume")

        # test 2: broken JSON recipe file.
        with self.subTest("test 2: broken JSON recipe file."):
            result, err = backbone.openjson("broken_for_testcase.json")
            self.assertEqual(
                err,
                "This is no valid JSON file. Try deleting comments.")
            self.assertIs(result, None)

        # test 3: file path wrong/ file does not exist
        with self.subTest("test 3: file path wrong/ file does not exist"):
            result, err = backbone.openjson("NoFileHere.json")
            self.assertEqual(err, "The file path or file name is incorrect.")
            self.assertIsNone(result)


    def test_jsonToRecipe(self):
        # test 1: Not giving a dict as input to jsonToRecipe
        with self.subTest("test 1: Not giving a dict as input to jsonToRecipe"):
            result, err = backbone.jsonToRecipe(None)
            self.assertIs(result, None)
            self.assertEqual(
                err,
                'Function jsonToRecipe expects dictionary as input.')

        # test 2: correct format with additional information still works
        with self.subTest("test 2: correct format with additional information still works"):
            data = {
                "nodes": [{
                    "name": "rectangle_area",
                    "inputs": {"d": "flavour.d", "b": "flavour.b"},
                    "unneccessary": "and of no interest",
                    "outputs": {"a": "area"},
                    "stepsource": "rectangle_area.py"
                }]
            }
            result, err = backbone.jsonToRecipe(data)
            self.assertIsInstance(result, backbone.Recipe)
            self.assertIsNone(err)
            self.assertEqual(result.nodes[0].inputs['b'], "flavour.b")

        # test 3: incorrect format
        with self.subTest("test 3: incorrect format"):
            data = {
                "nodes": [{
                    "name": "rectangle_area",
                    "missing": {},
                    "outputs": {"a": "area"},
                    "stepsource": "rectangle_area.py"
                }]
            }
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNone(result)
            self.assertEqual(err, 'Error while parsing json data into recipe object.')

        # test 4: Annoying the Node class:
        # list of inputs is interpreted as value for parameter "a"
        with self.subTest("list of inputs is interpreted as value for parameter \"a\""):
            data = {
                "nodes": [{
                    "name": "fancy",
                    "inputs": {"a": ["first", "second"]},
                    "outputs": {"a": "area"},
                    "stepsource": "collect"
                }]
            }
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNotNone(result)
            self.assertIsNone(err)

        # test 4: Annoying the Node class
        with self.subTest("test 4: Annoying the Node class"):
            data = {
                "nodes": [{
                    "name": "fancy",
                    "inputs": {"a": "first"},
                    "outputs": {"a": "area"},
                    "stepsource": "no_build-in_function"
                }]
            }
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNone(result)
            self.assertIsNotNone(err)

        # todo: versions of var data in object with expected result
        # and err value attached to it and loop for test execution!

    def test_inputIntegrity(self):
        # recipe with two outputs with same name
        with self.subTest("recipe with two outputs with same name"):
            data = {
                "nodes": [{
                    "name": "A",
                    "inputs": {},
                    "outputs": {"a": "doppleganger"},
                    "stepsource": "source.py"
                }, {
                    "name": "B",
                    "inputs": {},
                    "outputs": {"b": "doppleganger"},
                    "stepsource": "source.py"
                }]
            }
            recipe, err = backbone.jsonToRecipe(data)
            self.assertIsNone(err)
            err, warn = recipe.inputIntegrity()
            self.assertTrue(str(err).startswith('The output'))
            self.assertIsNone(warn)

        # recipe that should work correctly
        with self.subTest("recipe that should work correctly"):
            data = {
                "nodes": [{
                    "name": "A",
                    "inputs": {"a": "flavour.a", "b": "flavour.b"},
                    "outputs": {"c": "outOfA"},
                    "stepsource": "somesource.py"
                }, {
                    "name": "B",
                    "inputs": {"d": "flavour.d", "e": "flavour.e"},
                    "outputs": {"f": "outOfB"},
                    "stepsource": "source.py"
                }, {
                    "name": "C",
                    "inputs": {"g": "outOfA", "h": "outOfB"},
                    "outputs": {"i": "outOfC"},
                    "stepsource": "source.py"
                }, {
                    "name": "D",
                    "inputs": {"toBeCollected": "outOfC", "by": "flavour.e"},
                    "outputs": {"k": "collected"},
                    "stepsource": "collect"
                }]
            }
            recipe, err = backbone.jsonToRecipe(data)
            self.assertIsNone(err)
            err, warn = recipe.inputIntegrity()
            self.assertIsNone(err)
            self.assertIsNone(warn)
            self.assertEqual(len(recipe.nodes), 4)

        # recipe that has an unreachable node C that also makes D unreachable
        with self.subTest("recipe that has an unreachable node C that also makes D unreachable"):
            data = {
                "nodes": [{
                    "name": "A",
                    "inputs": {"a": "flavour.a", "b": "flavour.b"},
                    "outputs": {"c": "outOfA"},
                    "stepsource": "somesource.py"
                }, {
                    "name": "B",
                    "inputs": {"d": "flavour.d", "e": "flavour.e"},
                    "outputs": {"f": "outOfB"},
                    "stepsource": "source.py"
                }, {
                    "name": "C",
                    "inputs": {"g": "outOfA", "h": "unreachable"},
                    "outputs": {"i": "outOfC"},
                    "stepsource": "source.py"
                }, {
                    "name": "D",
                    "inputs": {"toBeCollected": "outOfC", "by": "flavour.e"},
                    "outputs": {"k": "collected"},
                    "stepsource": "collect"
                }]
            }
            recipe, err = backbone.jsonToRecipe(data)
            self.assertIsNone(err)
            err, warn = recipe.inputIntegrity()
            self.assertIsNone(err)
            self.assertIsNotNone(warn)
            self.assertEqual(len(recipe.nodes), 2)

        # look up file path for existence
        with self.subTest("look up file path for existence"):
            data = {
                "nodes": [{
                    "name": "A",
                    "inputs": {"a": "recipe.json"},
                    "outputs": {"c": "outOfA"},
                    "stepsource": "somesource.py"
                }]
            }
            recipe, err = backbone.jsonToRecipe(data)
            self.assertIsNone(err)
            err, warn = recipe.inputIntegrity()
            self.assertIsNone(err)
            self.assertIsNone(warn)
            self.assertEqual(len(recipe.nodes), 1)


#    #def test_findCircles():
#
#

    def test_recursiveDFS(self):
        # recipe with no loop
        with self.subTest("test 1: recipe with no loop"):
            data = {
                "nodes": [{
                    "name": "A",
                    "inputs": {"a": "flavour.a"},
                    "outputs": {"b": "outOfA"},
                    "stepsource": "somesource.py"
                }, {
                    "name": "B",
                    "inputs": {},
                    "outputs": {"final": "outOfB"},
                    "stepsource": "somesource.py"
                }, {
                    "name": "C",
                    "inputs": {"1": "outOfA", "2": "outOfB"},
                    "outputs": {"c": "outOfC"},
                    "stepsource": "somesource.py"
                }, {
                    "name": "D",
                    "inputs": {"1": "outOfC", "2": "outOfB"},
                    "outputs": {"c": "outOfD"},
                    "stepsource": "somesource.py"
                }]
            }
            recipe, err = backbone.jsonToRecipe(data)
            self.assertIsNone(err)
            result = recipe.findCircles()
            print(result)


class TestFlavour(unittest.TestCase):

    def test_readjson(self):
        # test 1: valid JSON flavour file.
        with self.subTest("test 1: valid JSON flavour file."):
            result, err = backbone.openjson("flavour.json")
            self.assertIsNone(err)
            self.assertEqual(result['fS'], 9.22e9)
            self.assertEqual(result['subsample'][0]['type'], 'range')
            self.assertEqual(result['average'][2], 64)
            self.assertEqual(result['tx_lfsr_tap'], "0x8F1")

    def test_Flavour_tostring(self):
        # only test: correct comparison string
        flavour = backbone.readflavour("flavour.json")
        with open("flavour_tostring.txt", "r") as f:
            comparisonStr = f.read()
            testedStr = flavour.tostring()
            self.assertEqual(testedStr, comparisonStr)

    def test_FileParamValue(self):
        # variables
        key = "RandomPasswordForFile"

        # test 1: valid input
        with self.subTest("test 1: valid file parameter"):
            filepath = "test.log"
            file_param = backbone.FileParamValue(filepath, key)

        # test 2: invalid filepath
        with self.subTest("test 2: invalid filepath"):
            filepath = "none_existing"
            with self.assertRaises(IOError):
                file_param = backbone.FileParamValue(filepath, key)

    def test_FileParamValue_tostring(self):
        # only test: correct comparison string
        file_param = backbone.FileParamValue("test.log", "no key")
        with open("file_param_tostring.txt", "r") as f:
            comparisonStr = f.read()
            testedStr = file_param.tostring()
            self.assertEqual(testedStr, comparisonStr)

    def test_Param(self):
        # variables
        # expected values of the parameters above for comparison
        fileparamvalue = backbone.FileParamValue("test.log", "")
        # test_entries contain name, entry, values, no_of_values, type
        test_entries = [
            { # entry 0
                "name": "file_entry",
                "entry": {
                    "type": "file",
                    "file": "resources/realtime-moving_DIV_4096.mat",
                    "key": "data"
                },
                "values": [fileparamvalue]
            },
            { # entry 1
                "name": "range_entry",
                "entry": {
                    "type": "range",
                    "start": 1,
                    "stop": 6,
                    "step": 1
                },
                "values": [1,2,3,4,5,6]
            },
            { # entry 2
                "name": "simple_entry",
                "entry": 9.22e9,
                "values": [9.22e9]
            },
            { # entry 3
                "name": "list_entry",
                "entry": [32, 64, 128],
                "values": [32, 64, 128]
            },
            { # entry 4
                "name": "composed_entry",
                "entry": [
                    {
                        "type": "range",
                        "start": 1,
                        "stop": 6,
                        "step": 1
                    },
                    32,
                    64,
                    128
                ],
                "values": [1, 2, 3, 4, 5, 6, 32, 64, 128]
            },
            { # entry 3
                "name": "list_entry",
                "entry": None,
                "values": []
            }
        ]

        # tests 0-4: all entry types, correct inputs, exceptions only occure in
        # the helper functions called by Param
        for nr in range(0,4):
            entry = test_entries[nr]
            param = backbone.Param(entry["name"], entry["entry"])
            for i in range(0, len(entry["values"])-1):
                with self.subTest(TestNr = nr, entryName = entry["name"], i = i):
                    self.assertEqual(param.values[i], entry["values"][i]) 

    def test_appendFileParam(self):
        # variables
        test_entries = [
            { # entry 0
                "file": "test.log",
                "key": "R4nd0m_P4ssw0rd",
            },
            { # entry 1
                "file": "test.log",
                "key": "",
            },
            { # entry 2
                "file": "test.log",
                "key": None,
            },
            { # entry 3
                "file": "test.log",
                "no_key_field": "",
            },
            { # entry 4
                "file": None,
                "key": "",
            },
            { # entry 5
                "file": "thisDoesNotExist.txt",
                "key": "R4nd0m_P4ssw0rd",
            },    
            { # entry 6
                "no_file_field": "",
                "key": "R4nd0m_P4ssw0rd",
            }
        ]
        no_file_entry = "There is no file given to the file param!"
        false_path = "The filepath to the file param does not exist."
        expected_outcomes = [
            [None],                      # entry 0
            [None],                      # entry 1
            [None],                      # entry 2
            [None],                      # entry 3
            [ValueError, false_path],    # entry 4
            [ValueError, false_path],    # entry 5
            [ValueError, no_file_entry]  # entry 6
        ]

        for i in range(0, 6):
            param = backbone.Param("Fresh empty param object", None)
            entry = test_entries[i]
            expect = expected_outcomes[i]
            with self.subTest(TestNr = i):
                if (expect[0] == None):
                    param.appendFileParam(entry)
                else:
                    with self.assertRaisesRegex(expect[0], expect[1]):
                        param.appendFileParam(entry)