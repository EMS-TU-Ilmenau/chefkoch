# -*- coding: utf-8 -*-
# Copyright 2019 Christoph Wagner
#     https://www.tu-ilmenau.de/it-ems/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
r"""
This file holds unit tests for all functions inside the chefkoch module to
ease the development process.
Execute this file by typing into a linux console in same directory:

python3 -m unittest test_chefkoch

(test_chefkoch.py depending on python and linux version)
The test runner executes all functions that start with test_[functionname].
Functions that start with check_[functionname] are helper functions.
The checks are for the recipe and flavour class and called by their tests.
Functions that start with assert_[functionname] are parameters used to
call a check function. They encapsulate the asserts of test results.

The test functions are using subtests to print the exact test case that
threw an error. Subtests are only available from python 3.4 on.
"""


import os
import unittest
import sys
import chefkoch.core as core
import chefkoch.recipe as backbone
import chefkoch.fridge as fridge
import chefkoch.container as container
import chefkoch.step as step
import numpy

# todo: Konsultiere Fabian

"""
class TestChefkoch(unittest.TestCase):
"""
"""
    This class includes functions that test both recipe and flavour class
    functions or are called by recipe or flavour tests.
    """
"""

    def test_readjson(self):
        result = chefkoch.readfile("recipe", "test/recipe.json")

    def check_openjson(self, file, assertionFunc):
        # not executed by the test runner but by the test_openjson functions
        # inside the TestRecipe class and the TestFlavour class
        if sys.version_info.micro > 8 or sys.version_info.minor > 6:
            # test 1: valid JSON recipe file.
            with self.subTest("test 1: Valid JSON file.", file=file):
                result = backbone.openjson(file)
                self.assertTrue(isinstance(result, dict))
                assertionFunc(result)

            # test 2: broken JSON recipe file.
            with self.subTest("test 2: broken JSON file."):
                with self.assertRaises(ValueError) as err:
                    result = backbone.openjson("test/broken_for_testcase.json")
                    self.assertEqual(
                        err,
                        "This is no valid JSON file. "
                        + "Try deleting comments.",
                    )

            # test 3: file path wrong/ file does not exist
            with self.subTest("test 3: file path wrong/ file does not exist"):
                with self.assertRaises(IOError) as err:
                    result = backbone.openjson("NoFileHere.json")
                    self.assertEqual(
                        err, "The file path or file name is incorrect."
                    )
        # for python 3.6.8 and previous do
        else:
            # test 1: valid JSON recipe file.
            result = backbone.openjson(file)
            self.assertTrue(isinstance(result, dict))
            assertionFunc(result)

            # test 2: broken JSON recipe file.
            with self.assertRaises(ValueError) as err:
                result = backbone.openjson("test/broken_for_testcase.json")
                self.assertEqual(
                    err, "This is no valid JSON file. Try deleting comments."
                )

            # test 3: file path wrong/ file does not exist
            with self.assertRaises(IOError) as err:
                result = backbone.openjson("NoFileHere.json")
                self.assertEqual(
                    err, "The file path or file name is incorrect."
                )


class TestRecipe(unittest.TestCase):
    def assert_openjson(self, result):
        # this is used to reuse the check_openjson both in the TestRecipe and
        # TestFlavour class without copy-pasting
        self.assertEqual(result["nodes"][1]["name"], "prisma_volume")

    def test_openjson(self):
        # test 1: valid JSON recipe file.
        test_chefkoch = TestChefkoch()
        test_chefkoch.check_openjson("test/recipe.json", self.assert_openjson)

    def test_jsonToRecipe(self):
        # correct data to be changed in every subtest
        correct_data = {
            "nodes": [
                {
                    "name": "rectangle_area",
                    "inputs": {"d": "flavour.d", "b": "flavour.b"},
                    "unneccessary": "and of no interest",
                    "outputs": {"a": "area"},
                    "stepsource": "rectangle_area.py",
                }
            ]
        }
        # test 1: Not giving a dict as input to jsonToRecipe
        with self.subTest(
            "test 1: Not giving a dict as input to jsonToRecipe"
        ):
            with self.assertRaises(TypeError):
                result = backbone.dictToRecipe(None)
                self.assertEqual(
                    err, "Function jsonToRecipe expects dictionary as input."
                )

        # test 2: correct format with additional information still works
        with self.subTest(
            "test 2: correct format with additional information still works"
        ):
            result = backbone.dictToRecipe(correct_data)
            self.assertIsInstance(result, backbone.Recipe)
            self.assertEqual(result.nodes[0].inputs["b"], "flavour.b")

        # test 3: incorrect format
        with self.subTest("test 3: incorrect format"):
            data = correct_data
            data["nodes"][0].pop("inputs")
            with self.assertRaises(KeyError) as err:
                result = backbone.dictToRecipe(data)
                self.assertEqual(
                    err, "Error while parsing json data into recipe object."
                )

        # test 4: Annoying the Node class:
        # list of inputs is interpreted as value for parameter "a"
        with self.subTest(
            'list of inputs is interpreted as value for parameter "a"'
        ):
            data = correct_data
            data["nodes"][0]["inputs"] = {"a": ["first", "second"]}
            result = backbone.dictToRecipe(data)
            self.assertIsNotNone(result)

        # test 4: Annoying the StepSource class
        with self.subTest("test 4: Annoying the Node class"):
            data = correct_data
            data["nodes"][0]["stepsource"] = "no_built-in_function"
            with self.assertRaises(TypeError):
                result = backbone.dictToRecipe(data)

    def test_inputIntegrity(self):
        # recipe with two outputs with same name
        with self.subTest("recipe with two outputs with same name"):
            data = {
                "nodes": [
                    {
                        "name": "A",
                        "inputs": {},
                        "outputs": {"a": "doppleganger"},
                        "stepsource": "source.py",
                    },
                    {
                        "name": "B",
                        "inputs": {},
                        "outputs": {"b": "doppleganger"},
                        "stepsource": "source.py",
                    },
                ]
            }
            recipe = backbone.dictToRecipe(data)
            with self.assertRaises(NameError) as err:
                recipe.inputIntegrity()
                self.assertTrue(str(err).startswith("The output"))

        # recipe that should work correctly
        with self.subTest("Recipe that should work correctly"):
            data = {
                "nodes": [
                    {
                        "name": "A",
                        "inputs": {"a": "flavour.a", "b": "flavour.b"},
                        "outputs": {"c": "outOfA"},
                        "stepsource": "somesource.py",
                    },
                    {
                        "name": "B",
                        "inputs": {"d": "flavour.d", "e": "flavour.e"},
                        "outputs": {"f": "outOfB"},
                        "stepsource": "source.py",
                    },
                    {
                        "name": "C",
                        "inputs": {"g": "outOfA", "h": "outOfB"},
                        "outputs": {"i": "outOfC"},
                        "stepsource": "source.py",
                    },
                    {
                        "name": "D",
                        "inputs": {
                            "toBeCollected": "outOfC",
                            "by": "flavour.e",
                        },
                        "outputs": {"k": "collected"},
                        "stepsource": "collect",
                    },
                ]
            }
            recipe = backbone.dictToRecipe(data)
            recipe.inputIntegrity()
            self.assertEqual(len(recipe.nodes), 4)

        # recipe that has an unreachable node C that also makes D unreachable
        with self.subTest(
            "recipe that has an unreachable node C which makes D unreachable"
        ):
            data = {
                "nodes": [
                    {
                        "name": "A",
                        "inputs": {"a": "flavour.a", "b": "flavour.b"},
                        "outputs": {"c": "outOfA"},
                        "stepsource": "somesource.py",
                    },
                    {
                        "name": "B",
                        "inputs": {"d": "flavour.d", "e": "flavour.e"},
                        "outputs": {"f": "outOfB"},
                        "stepsource": "source.py",
                    },
                    {
                        "name": "C",
                        "inputs": {"g": "outOfA", "h": "unreachable"},
                        "outputs": {"i": "outOfC"},
                        "stepsource": "source.py",
                    },
                    {
                        "name": "D",
                        "inputs": {
                            "toBeCollected": "outOfC",
                            "by": "flavour.e",
                        },
                        "outputs": {"k": "collected"},
                        "stepsource": "collect",
                    },
                ]
            }
            recipe = backbone.dictToRecipe(data)
            recipe.inputIntegrity()
            self.assertEqual(len(recipe.nodes), 2)

        # look up file path for existence
        with self.subTest("look up file path for existence"):
            data = {
                "nodes": [
                    {
                        "name": "A",
                        "inputs": {"a": "test/recipe.json"},
                        "outputs": {"c": "outOfA"},
                        "stepsource": "somesource.py",
                    }
                ]
            }
            recipe = backbone.dictToRecipe(data)
            recipe.inputIntegrity()
            self.assertEqual(len(recipe.nodes), 1)

    #    #def test_findCircles():
    #
    #

    def test_recursiveDFS(self):
        # recipe with no loop
        with self.subTest("test 1: recipe with no loop"):
            data = {
                "nodes": [
                    {
                        "name": "A",
                        "inputs": {"a": "flavour.a"},
                        "outputs": {"b": "outOfA"},
                        "stepsource": "somesource.py",
                    },
                    {
                        "name": "B",
                        "inputs": {},
                        "outputs": {"final": "outOfB"},
                        "stepsource": "somesource.py",
                    },
                    {
                        "name": "C",
                        "inputs": {"1": "outOfA", "2": "outOfB"},
                        "outputs": {"c": "outOfC"},
                        "stepsource": "somesource.py",
                    },
                    {
                        "name": "D",
                        "inputs": {"1": "outOfC", "2": "outOfB"},
                        "outputs": {"c": "outOfD"},
                        "stepsource": "somesource.py",
                    },
                ]
            }
            recipe = backbone.dictToRecipe(data)
            result = recipe.findCircles()
            print(result)


class TestFlavour(unittest.TestCase):
    def test_readjson(self):
        # test 1: valid JSON flavour file.
        with self.subTest("test 1: valid JSON flavour file."):
            result = backbone.openjson("test/flavour.json")
            self.assertEqual(result["fS"], 9.22e9)
            self.assertEqual(result["subsample"][0]["type"], "range")
            self.assertEqual(result["average"][2], 64)
            self.assertEqual(result["tx_lfsr_tap"], "0x8F1")

    def test_Flavour_tostring(self):
        # only test: correct comparison string
        flavour = backbone.readflavour("test/flavour.json")
        with open("test/flavour_tostring.txt", "r") as f:
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
        with open("test/file_param_tostring.txt", "r") as f:
            comparisonStr = f.read()
            testedStr = file_param.tostring()
            self.assertEqual(testedStr, comparisonStr)

    def test_Param_and_appendEntry(self):
        # variables
        # expected values of the parameters above for comparison
        fileparamvalue = backbone.FileParamValue("test.log", "")
        # test_entries contain name, entry, values, no_of_values, type
        test_entries = [
            {  # entry 0
                "name": "file_entry",
                "entry": {
                    "type": "file",
                    "file": "resources/realtime-moving_DIV_4096.mat",
                    "key": "data",
                },
                "values": [fileparamvalue],
            },
            {  # entry 1
                "name": "range_entry",
                "entry": {"type": "range", "start": 1, "stop": 6, "step": 1},
                "values": [1, 2, 3, 4, 5, 6],
            },
            {  # entry 2
                "name": "simple_entry",
                "entry": 9.22e9,
                "values": [9.22e9],
            },
            {"name": "empty_entry", "entry": None, "values": []},  # entry 3
            {  # entry 4
                "name": "list_entry",
                "entry": [32, 64, 128],
                "values": [32, 64, 128],
            },
            {  # entry 5
                "name": "composed_entry",
                "entry": [
                    {"type": "range", "start": 1, "stop": 6, "step": 1},
                    32,
                    64,
                    128,
                ],
                "values": [1, 2, 3, 4, 5, 6, 32, 64, 128],
            },
        ]

        # tests 0-4: Param constructor, all entry types, correct inputs
        # exceptions only occure in the helper functions called by Param
        for nr in range(0, 5):
            entry = test_entries[nr]
            param = backbone.Param(entry["name"], entry["entry"])
            for i in range(0, len(entry["values"]) - 1):
                with self.subTest(TestNr=nr, entryName=entry["name"], i=i):
                    self.assertEqual(param.values[i], entry["values"][i])
            # I don't want to declare the same test_entries again, so here comes
            # test_appendEntry
        for nr in range(0, 3):
            entry = test_entries[nr]
            param = backbone.Param("Fresh param object", [])
            for i in range(0, len(entry["values"]) - 1):
                with self.subTest(TestNr=nr, entryName=entry["name"], i=i):
                    param.appendEntry(entry["entry"])
                    self.assertEqual(param.values[i], entry["values"][i])

    def test_appendFileParam(self):
        # variables
        test_entries = [
            {"file": "test.log", "key": "R4nd0m_P4ssw0rd", },  # entry 0
            {"file": "test.log", "key": "", },  # entry 1
            {"file": "test.log", "key": None, },  # entry 2
            {"file": "test.log", "no_key_field": "", },  # entry 3
            {"file": None, "key": "", },  # entry 4
            {
                "file": "thisDoesNotExist.txt",
                "key": "R4nd0m_P4ssw0rd",
            },  # entry 5
            {"no_file_field": "", "key": "R4nd0m_P4ssw0rd", },  # entry 6
        ]
        no_file_entry = "There is no file given to the file param!"
        false_path = "The filepath to the file param does not exist."
        expected_outcomes = [
            [None],  # entry 0
            [None],  # entry 1
            [None],  # entry 2
            [None],  # entry 3
            [ValueError, false_path],  # entry 4
            [ValueError, false_path],  # entry 5
            [ValueError, no_file_entry],  # entry 6
        ]

        for i in range(0, 6):
            param = backbone.Param("Fresh empty param object", None)
            entry = test_entries[i]
            expect = expected_outcomes[i]
            with self.subTest(TestNr=i):
                if expect[0] is None:
                    param.appendFileParam(entry)
                else:
                    with self.assertRaisesRegex(expect[0], expect[1]):
                        param.appendFileParam(entry)

    def test_appendValuesFromRange(self):
        # test cases
        test_entries = [
            {"start": 1, "stop": 6, "step": 1, "expect": 6},  # entry 0
            {"start": -1, "stop": -6, "step": -1, "expect": 6},  # entry 1
            {"start": -10, "stop": 20, "step": 1, "expect": 31},  # entry 2
            {"start": 10, "stop": -10, "step": -1, "expect": 21},  # entry 3
            {"start": -3, "stop": 3, "step": 0.5, "expect": 13},  # entry 4
            {"start": 0, "stop": 1, "step": 0.125, "expect": 9},  # entry 5
            # invalid values from here:
            {  # entry 6
                "start": "hell",
                "stop": "hellooooooooo",
                "step": "o",
                "expect": 0,
            },
            {"start": "a", "stop": "f", "step": 1, "expect": 0},  # entry 7
            {"start": -1, "stop": -6, "step": 1, "expect": 0},  # entry 8
            {"start": 1, "stop": 10, "step": -1, "expect": 0},  # entry 9
        ]

        for i in range(0, 9):
            entry = test_entries[i]
            entry["type"] = "range"
            param = backbone.Param("Fresh empty param object", [])
            with self.subTest(
                TestNr=i,
                start=entry["start"],
                stop=entry["stop"],
                step=entry["step"],
            ):
                param.appendValuesFromRange(entry)
                self.assertEqual(len(param.values), entry["expect"])

    def test_readflavour(self):
        # only test: parsing the whole file
        with self.subTest("test 1: valid JSON flavour file."):
            flavour = backbone.readflavour("test/flavour.json")
            self.assertEqual(flavour["fS"].values[0], 9.22e9)
            self.assertEqual(len(flavour["subsample"].values), 19)
            self.assertEqual(flavour["average"].values[2], 3)
            self.assertEqual(flavour["tx_lfsr_tap"].values[0], "0x8F1")

    # todo: some day flavour['fS'] should return flavour['fS'].values[0] if
    # there's only one entry to the parameter fS
    # todo: some day flavour['fS'] should return flavour['fS'].values if there
    # is more then one entry to the parameter fS

    def assert_openjson(self, result):
        # this is used to reuse the check_openjson both in the TestRecipe and
        # TestFlavour class without copy-pasting
        self.assertEqual(result["data"]["type"], "file")

    def test_openjson(self):
        # using three tests in TestChefkoch
        test_chefkoch = TestChefkoch()
        test_chefkoch.check_openjson("test/flavour.json", self.assert_openjson)

    def test_jsonToFlavour(self):
        # correct data to be changed in every subtest
        # TODO! copy correct_data into data, do not hand over the link!
        data = {
            "singleVal": 10.33e3,
            "fileVal": {
                "type": "file",
                "file": "test.log",
                "key": "",
                "unnecessary": "something",
            },
            "listVal": [32, 64, 128],
            "rangeVal": {"type": "range", "start": 1, "stop": 5, "step": 1},
        }
        # test 1: Not giving a dict as input to jsonToRecipe
        with self.subTest(
            "test 1: Not giving a dict as input to jsonToRecipe"
        ):
            with self.assertRaises(TypeError) as err:
                result = backbone.dictToFlavour(None)
                self.assertEqual(
                    err,
                    "Function jsonToFlavour expects a dictionary as input.",
                )

        # test 2: correct format with additional information still works
        with self.subTest(
            "test 2: correct format with additional information still works"
        ):
            result = backbone.dictToFlavour(data)
            self.assertIsInstance(result, backbone.Flavour)
            self.assertEqual(result["singleVal"].values[0], 10.33e3)
            self.assertEqual(result["fileVal"].values[0].file, "test.log")
            self.assertEqual(len(result["rangeVal"].values), 5)

        # test 3: File does not exist
        with self.subTest("test 3: File does not exist"):
            data["fileVal"]["file"] = "no_existing_file.txt"
            result = backbone.dictToFlavour(data)
            # todo how can I check if there was a warning?
            # todo delete empty parameters until following:
            with self.assertRaises(KeyError):
                result["fileVal"]

        # test 4: Annoying the Input integrity tests
        with self.subTest("test 4: Giving no known name as type"):
            data["fileVal"]["type"] = "no actual type"
            result = backbone.dictToFlavour(data)

        # test 5: incorrect format
        with self.subTest("test 5: Having no type field"):
            data["fileVal"].pop("type")
            result = backbone.dictToFlavour(data)
"""
# Results for comparing and using
config_dict = {
    "options": {"test": True, "directory": False, "configOut": True},
    "resource": {
        "raw_data": "resource/raw_data.npy",
        "tex_paper": "resource/paper",
    },
    "flavour": {
        "num_lambda": [
            {
                "type": "log",
                "start": "1e-3",
                "stop": "1e3",
                "count": 7,
                "base": 10,
            },
            {"type": "log", "start": "1e7", "stop": "1e19", "count": 5},
            {"type": "lin", "start": 8, "stop": 12, "step": 1},
        ],
        "num_N": {"type": "lin", "start": 10, "stop": 20, "step": 2},
        "num_K": [1, 2, 3, 7, 8],
        "algorithm": ["BP", "OMP", "ISTA", "FISTA", "TWISTA"],
    },
    "kitchen": {"stove": "local"},
    "recipe": {
        "compute_a": {
            "type": "python",
            "resource": "steps/dosomething.py",
            "inputs": {"some_parameters": "num_K"},
            "outputs": {"result": "z"},
        },
        "doItTwice_z": {
            "type": "python",
            "resource": "steps/step2.py",
            "inputs": {"data": "z"},
            "outputs": {"result": "seconds"},
        },
    },
    "link": {
        "figure_z": "results/figures/figure_z.pdf",
        "paper": "results/paper.pdf",
    },
    "targets": "all",
}

path = "./testdirectory"


class TestConfiguration(unittest.TestCase):
    # so funktioniert das wahrscheinlich nicht
    def test_init(self):
        self.cheffile = container.YAMLContainer(path + "/cheffile.yml")
        arg = {
            "targets": None,
            "options": None,
            "cheffile": None,
            "resource": None,
            "flavour": None,
            "kitchen": None,
            "recipe": None,
            "link": None,
        }
        # self.chef = core.Chefkoch(cheffile, arg)
        self.configuration = core.Configuration(self.cheffile, path, arg)
        self.assertEqual(config_dict, self.configuration.items)


class TestFridge(unittest.TestCase):
    """
    Testcases for the functionality of the fridge
    """

    # das ist vermutlich unnötig
    resource = {
        "num_lambda": [
            {
                "type": "log",
                "start": "1e-3",
                "stop": "1e3",
                "count": 7,
                "base": 10,
            },
            {"type": "log", "start": "1e7", "stop": "1e19", "count": 5},
            {"type": "lin", "start": 8, "stop": 12, "step": 1},
        ],
        "num_N": {"type": "lin", "start": 10, "stop": 20, "step": 2},
        "num_K": [1, 2, 3, 7, 8],
        "algorithm": ["BP", "OMP", "ISTA", "FISTA", "TWISTA"],
    }

    def setUp(self):
        self.fridge = fridge.Fridge(config_dict, path)

    def test_fridge_makeFlavours(self):
        # test
        self.fridge.makeFlavours(config_dict["flavour"])

        # items = self.fridge.shelfs["flavours"].items
        flavour_result = {
            "num_lambda": [
                0.001,
                0.01,
                0.1,
                1.0,
                10.0,
                100,
                1000,
                10000000.0,
                10000000000.0,
                10000000000000.0,
                1e16,
                1e19,
                8,
                9,
                10,
                11,
                12,
            ],
            "num_N": [10, 12, 14, 16, 18, 20],
            "num_K": [1, 2, 3, 7, 8],
            "algorithm": ["BP", "OMP", "ISTA", "FISTA", "TWISTA"],
        }
        for x in flavour_result:
            if isinstance(self.fridge.shelves[x].items[0], str):
                self.assertEqual(
                    self.fridge.shelves[x].items, flavour_result[x]
                )
            else:
                i = 0
                for element in flavour_result[x]:
                    self.assertAlmostEqual(
                        element, self.fridge.shelves[x].items[i], places=7
                    )
                    i = i + 1

    def test_fridge_makeResources(self):
        # Ressources in cheffile defined
        self.fridge.makeResources(config_dict["resource"], False)
        resources = ["raw_data", "tex_paper"]
        for x in resources:
            assert x in self.fridge.shelves
        # Ressources in recipe defined
        self.fridge.makeResources(config_dict["recipe"], True)
        resources_recipe = ["compute_a", "doItTwice_z"]
        for x in resources_recipe:
            assert x in self.fridge.shelves

    def test_fridge_makeItemShelves(self):
        self.fridge.makeItemShelves(["z", "seconds"])
        items = ["z", "seconds"]
        for x in items:
            assert x in self.fridge.shelves

        with self.assertRaises(Exception) as context:
            self.fridge.makeItemShelves(["z"])

        self.assertTrue(
            "z already exists in this fridge!" in str(context.exception)
        )

    def test_getItem(self):
        # test for failing
        testFalse = "nope"
        with self.assertRaises(Exception) as context:
            self.fridge.getItem(testFalse)

        self.assertTrue(str(testFalse) + " doesn't exist in this fridge")

        # test for correct behaviour falvour
        self.fridge.makeFlavours(config_dict["flavour"])
        testTrue = "num_K"
        result = self.fridge.getItem(testTrue)
        self.assertEqual(result, [1, 2, 3, 7, 8])

        # TODO: Test for correct behaviour with items


class TestStepPython(unittest.TestCase):
    """
    Tests for checking the correct behaviour of a python-step
    """

    def setUp(self):
        # appending correct module-path
        sys.path.append(str(path) + "/steps/")
        self.logger = core.Logger(config_dict)
        self.fridge = fridge.Fridge(config_dict, path)
        # self.fridge.makeResources(config_dict["resource"], False)
        self.fridge.makeResources(config_dict["recipe"], True)
        self.fridge.makeFlavours(config_dict["flavour"])
        self.step = step.StepPython(
            self.fridge.shelves["compute_a"], {}, self.logger
        )
        # missing the dependencies

    def test_executeStep(self):
        self.step.executeStep()
        r = self.fridge.shelves["compute_a"].items["result"].result
        expected = [2, 3, 4, 8, 9]
        self.assertEqual(r, expected)


class TestStepShell(unittest.TestCase):
    """
    Tests for checking the correct behaviour of a python-step
    """

    def setUp(self):
        # appending correct module-path
        sys.path.append(str(path) + "/steps/")
        self.fridge = fridge.Fridge(config_dict, path)
        # self.fridge.makeResources(config_dict["resource"], False)
        self.fridge.makeResources(config_dict["recipe"], True)
        self.fridge.makeFlavours(config_dict["flavour"])
        # self.step = step.StepPython(self.fridge.shelves["compute_a"], {})

    def test_executeStep(self):
        pass
