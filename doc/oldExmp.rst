Examples used for the first version of chefkoch
================================================


A minimal work example for chefkoch can be found at

	https://gitlab.tu-ilmenau.de/FakEI/InIT/it-ems/Projects/PRIME/chefkoch-mwe

It has example files for a simulation. Some files are a little bit outdated, therefore
the following files state the current standards.

Inputs to chefkoch are made via command line. After installing it via::

	...> pip install chefkoch

there is a bunch of commands available. For example, use::

	...> chef version

to see if your chef installation worked.

Making inputs to chefkoch mostly happens through reading in files. For example, the
recipe, the overall simulation workflow, can be given to chefkoch via::

	...> chef read recipe filepath/recipe.json

The data format for the recipe file is JSON. The outer structure is a list, that contains
simulation steps, represented as nodes. Here is an example of how a recipe file might look
like::

    {
      "nodes": [ 
        {
          "name": "Think_Before_You_Speak", 
          "inputs": {"hi": "hello", "there": "world"},
          "outputs": {"combinedWords": "greeting"},
          "stepsource": "combine-words.py"
        },
        {
          "name": "Speak_Out_Loud",
          "inputs": {"something2say": "greeting"},
          "outputs": {},
          "stepsource": "print_string.py"
        }
      ]
    }

Granted, using chef is a little overkill to print "Hello World", but let's use it for an 
example. Each node in the list represents a simulation step. The name is a string, inputs and
outputs are given in a dictionary. The keys to the dictionary must be named as the input that
the function inside the stepsource takes. There are two possibilities for the values inside
the dictionary. The first one is to reference a parameter, that is defined in the flavour file
like "flavour.hello" or "flavour.world". The second possibility is an output of another step like
"greeting" is an output of `Think_Before_You_Speak` and an input to `Speak_Out_Loud`. Inputs and
outputs can be an empty dictionary. The stepsource can be a python function or a built-in function.

The inputs and outputs refering to a parameter are held in the flavour file. Here's an example on
how a flavour file might look like::

    {
      "hello": ["Hello", "Hi", "Good day", "Dear"],
      "world": ["there!", "World!", "ladies and gentleman."]
    }

But Parameters can also have single values, a range, hold a dictionary or a file or combinations of
them::

    {
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

Examples for the recipe or flavour file can be found in chefkoch/tests/.

