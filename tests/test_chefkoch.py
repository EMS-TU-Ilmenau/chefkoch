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

    def check_openjson(self, file, comparisonFunc):
        # not executed by the test runner but by the test_openjson functions
        # inside the TestRecipe class and the TestFlavour class
        # test 1: valid JSON recipe file.
        with self.subTest("test 1: Valid JSON file.", file = file):
            result, err = backbone.openjson(file)
            self.assertTrue(isinstance(result, dict))
            self.assertIsNone(err)
            comparisonFunc(result)

        # test 2: broken JSON recipe file.
        with self.subTest("test 2: broken JSON file."):
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

class TestRecipe(unittest.TestCase):

    def assert_openjson(self, result):
        # this is used to reuse the check_openjson both in the TestRecipe and
        # TestFlavour class without copy-pasting
        self.assertEqual(result['nodes'][1]['name'], "prisma_volume")
    
    def test_openjson(self):
        # test 1: valid JSON recipe file.
        test_chefkoch = TestChefkoch()
        test_chefkoch.check_openjson("recipe.json", self.assert_openjson)

    def test_jsonToRecipe(self):
        # correct data to be changed in every subtest
        correct_data = {
            "nodes": [{
                "name": "rectangle_area",
                "inputs": {"d": "flavour.d", "b": "flavour.b"},
                "unneccessary": "and of no interest",
                "outputs": {"a": "area"},
                "stepsource": "rectangle_area.py"
            }]
        }
        # test 1: Not giving a dict as input to jsonToRecipe
        with self.subTest("test 1: Not giving a dict as input to jsonToRecipe"):
            result, err = backbone.jsonToRecipe(None)
            self.assertIs(result, None)
            self.assertEqual(
                err,
                'Function jsonToRecipe expects dictionary as input.')

        # test 2: correct format with additional information still works
        with self.subTest("test 2: correct format with additional information still works"):
            result, err = backbone.jsonToRecipe(correct_data)
            self.assertIsInstance(result, backbone.Recipe)
            self.assertIsNone(err)
            self.assertEqual(result.nodes[0].inputs['b'], "flavour.b")

        # test 3: incorrect format
        with self.subTest("test 3: incorrect format"):
            data = correct_data
            data['nodes'][0].pop("inputs")
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNone(result)
            self.assertEqual(err, 'Error while parsing json data into recipe object.')

        # test 4: Annoying the Node class:
        # list of inputs is interpreted as value for parameter "a"
        with self.subTest("list of inputs is interpreted as value for parameter \"a\""):
            data = correct_data
            data['nodes'][0]['inputs'] = {"a": ["first", "second"]}
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNotNone(result)
            self.assertIsNone(err)

        # test 4: Annoying the Node class
        with self.subTest("test 4: Annoying the Node class"):
            data = correct_data
            data['nodes'][0]['stepsource'] = "no_built-in_function"
            result, err = backbone.jsonToRecipe(data)
            self.assertIsNone(result)
            self.assertIsNotNone(err)

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
        flavour, err = backbone.readflavour("flavour.json")
        self.assertIsNone(err)
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

    def test_Param_and_appendEntry(self):
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
                "name": "empty_entry",
                "entry": None,
                "values": []
            },
            { # entry 4
                "name": "list_entry",
                "entry": [32, 64, 128],
                "values": [32, 64, 128]
            },
            { # entry 5
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
            }
        ]

        # tests 0-4: Param constructor, all entry types, correct inputs
        # exceptions only occure in the helper functions called by Param
        for nr in range(0,5):
            entry = test_entries[nr]
            param = backbone.Param(entry["name"], entry["entry"])
            for i in range(0, len(entry["values"])-1):
                with self.subTest(TestNr = nr, entryName = entry["name"], i = i):
                    self.assertEqual(param.values[i], entry["values"][i]) 
            # I don't want to declare the same test_entries again, so here comes
            # test_appendEntry
        for nr in range(0,3):
            entry = test_entries[nr]
            param = backbone.Param("Fresh param object", [])
            for i in range(0, len(entry["values"])-1):
                with self.subTest(TestNr = nr, entryName = entry["name"], i = i):
                    param.appendEntry(entry["entry"]) 
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

    def test_appendValuesFromRange(self):
        # test cases
        test_entries = [
            { # entry 0
                "start": 1,
                "stop": 6,
                "step": 1,
                "expect": 6
            },
            { # entry 1
                "start": -1,
                "stop": -6,
                "step": -1,
                "expect": 6
            },
            { # entry 2
                "start": -10,
                "stop": 20,
                "step": 1,
                "expect": 31
            },
            { # entry 3
                "start": 10,
                "stop": -10,
                "step": -1,
                "expect": 21
            },
            { # entry 4
                "start": -3,
                "stop": 3,
                "step": 0.5,
                "expect": 13
            },
            { # entry 5
                "start": 0,
                "stop": 1,
                "step": 0.125,
                "expect": 9
            },
            # invalid values from here:
            { # entry 6
                "start": "hell",
                "stop": "hellooooooooo",
                "step": "o",
                "expect": 0
            },
            { # entry 7
                "start": "a",
                "stop": "f",
                "step": 1,
                "expect": 0
            },
            { # entry 8
                "start": -1,
                "stop": -6,
                "step": 1,
                "expect": 0
            },
            { # entry 9
                "start": 1,
                "stop": 10,
                "step": -1,
                "expect": 0
            }
        ]

        for i in range(0,9):
            entry = test_entries[i]
            entry['type'] = "range"
            param = backbone.Param("Fresh empty param object", [])
            with self.subTest(TestNr = i, start = entry["start"], stop = entry["stop"], step = entry["step"]):
                param.appendValuesFromRange(entry)
                self.assertEqual(len(param.values), entry['expect'])

    def test_readflavour(self):
        # only test: parsing the whole file
         with self.subTest("test 1: valid JSON flavour file."):
            flavour, err = backbone.readflavour("flavour.json")
            self.assertIsNone(err)
            self.assertEqual(flavour['fS'].values[0], 9.22e9)
            self.assertEqual(len(flavour['subsample'].values), 19)
            self.assertEqual(flavour['average'].values[2], 3)
            self.assertEqual(flavour['tx_lfsr_tap'].values[0], "0x8F1")
        # todo: some day flavour['fS'] should return flavour['fS'].values[0] if there's
        # only one entry to the parameter fS
        # todo: some day flavour['fS'] should return flavour['fS'].values if there is more
        # then one entry to the parameter fS

    def assert_openjson(self, result):
        # this is used to reuse the check_openjson both in the TestRecipe and
        # TestFlavour class without copy-pasting
        self.assertEqual(result['data']['type'], "file")
    
    def test_openjson(self):
        # using three tests in TestChefkoch
        test_chefkoch = TestChefkoch()
        test_chefkoch.check_openjson("flavour.json", self.assert_openjson)

    def test_jsonToFlavour(self):
        # correct data to be changed in every subtest
        # TODO! copy correct_data into data, do not hand over the link!
        data = {
            "singleVal": 10.33e3,
            "fileVal": {
                "type": "file",
                "file": "test.log",
                "key": "",
                "unnecessary": "something"
            },
            "listVal": [32, 64, 128],
            "rangeVal": {
                "type": "range",
                "start": 1,
                "stop": 5,
                "step": 1
            }
        }
        # test 1: Not giving a dict as input to jsonToRecipe
        with self.subTest("test 1: Not giving a dict as input to jsonToRecipe"):
            result, err = backbone.jsonToFlavour(None)
            self.assertIs(result, None)
            self.assertEqual(
                err,
                'Function jsonToFlavour expects a dictionary as input.')

        # test 2: correct format with additional information still works
        with self.subTest("test 2: correct format with additional information still works"):
            result, err = backbone.jsonToFlavour(data)
            self.assertIsInstance(result, backbone.Flavour)
            self.assertIsNone(err)
            self.assertEqual(result["singleVal"].values[0], 10.33e3)
            self.assertEqual(result["fileVal"].values[0].file, "test.log")
            self.assertEqual(len(result["rangeVal"].values), 5)

        # test 3: File does not exist
        with self.subTest("test 3: File does not exist"):
            data['fileVal']['file'] = "no_existing_file.txt"
            result, err = backbone.jsonToFlavour(data)
            self.assertIsNotNone(result)
            self.assertIsNone(err)
            # todo how can I check if there was a warning?
            # todo delete empty parameters until following:
            with self.assertRaises(KeyError):
                result['fileVal']

        # test 4: Annoying the Input integrity tests
        with self.subTest("test 4: Giving no known name as type"):
            data['fileVal']['type'] = "no actual type"
            result, err = backbone.jsonToFlavour(data)
            self.assertIsNotNone(result)
            self.assertIsNone(err)
            # todo catch warning

        # test 3: incorrect format
        with self.subTest("test 5: Having no type field"):
            data['fileVal'].pop("type")
            result, err = backbone.jsonToFlavour(data)
            self.assertIsNotNone(result)
            self.assertIsNone(err)
        