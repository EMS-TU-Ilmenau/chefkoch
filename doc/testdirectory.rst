Testdirectory
==============

The testdirectory includes examples of all files, you will need to start chefkoch
and are used by the automated tests.

Before you start chefkoch, you will need a testdirectory.
This directory should contain several files, most important the cheffile. All configuration files are written in yaml.

.. code-block::
	
	/
	|-- cheffile
	|-- [optional] recipe
	|-- [optional] kitchenfile
	|-- [optional] flavourfile
	|-- [optional] resourcefile
	|-- [optional] optionfile
	|-- cheffile.log
	|-- fridge
	|   |-- compute_a
	|   |   |-- 4b800a27 --> /steps/dosomething.py
	|   |   |-- 4b800a27.json
	|   |-- compile_latex
	|   |   |-- 82bba098 --> /steps/compile_latex.sh
	|   |   |-- 82bba098.json
	|   |-- figure_z
	|   |   |-- 4b800a27
	|   |   |-- 4b800a27.json
	|   |   |-- 4b800a27.log
	|   |-- paper
	|   |   |-- 86eaa918
	|   |   |-- 86eaa918.json
	|   |   |-- 86eaa918.log
	|   |-- tex_paper
	|   |   |-- 0029ffbe (tar-ball, basierend auf /resources/tex_paper)
	|   |   |-- 0029ffbe.json
	|   |-- raw_data
	|   |   |-- 31778bfc --> /resources/raw_data.npy
	|   |   |-- 31778bfc.json
	|   |-- render_figure_z:
	|   |   |-- bffc8273 --> /steps/render_figure.py
	|   |   |-- bffc8273.json
	|   |-- z
	|       |-- 5591b00c
	|       |-- 5591b00c.json
	|       |-- 5591b00c.log
	|-- resources
	|   |-- raw_data.npy
	|   |-- paper
	|       |-- paper.tex
	|       |-- paper.bib
	|-- results
	|   |-- figures
	|   |   |-- figure_z.pdf --> /fridge/figure_z/4b800a27
	|   |-- paper --> /fridge/paper/86eaa918
	|-- steps
		|-- compile_latex.sh
		|-- dosomething.py
		|-- render_figure.py

cheffile
---------
By default chefkoch assumes all configuration is stored in a file named `cheffile`. This assumption may be overridden via the command line.
The cheffile can also link to other files for certain information. So the other listed files are not strictly necessary, but it's more manageable to use multiple files.

It should contain the options, resources, flavours, kitchenfile, the recipe, and links.

.. code-block::

	options: "/options.yml"

	resource:
	beampatternLog: resources/beampatternLog.npy
	example_dir: resources/example_dir

	# recipe: !include "recipe.yml"

	flavour: "/flavour.yml"

	kitchen: "/kitchen.yml"

	recipe: "/recipe.yml"

	link:
	figure_z: results/figures/figure_z.pdf
	paper: results/paper.pdf
 
options and resources
----------------------

The options include:
	* directory: should the fridge be a folder structure
	* configOut: printing the complete config as file
	* debugLevel: setting the debugLevel

Resources decribe where to find the information which should be worked on.
It's equivalent to the raw data. 

flavour
--------

The next thing should be the flavour-file.
As is true for cooking, most pizza are baked using the same, simple steps. However, the wide range of gustatoric nuances is achieved through slight variations during the process itself, affecting taste and texture of the resulting dish greatly.
In this conceptual similarity, the flavour definition of a chefkoch recipe relates to variations of a set of parameters.

This could look like this, for example:
.. code-block::

	num_lambda:
		# These entries are the entries in the Configuration object:
		- {type: log, start: 1e-3, stop: 1e3, count: 7, base: 10}
		- {type: log, start: 1e7, stop: 1e19, count: 5}
		- {type: lin, start: 8, stop: 12, step: 1}
	# exemplary entry in the corresponding FlavourShelf 'num_lambda': [1e-3, 0.01, 0.1, 1., 8, 9, 10., 11, 12, 100., 1e3, 1e7, 1e10, 1e13, 1e16, 1e19]

	num_N:
		# These entries are the entries in the Configuration object
		type: lin
		start: 10
		stop: 20
		step: 2
	# exemplary entry in the corresponding FlavourShelf 'num_N': [10, 12, 14, 16, 18, 20]

	num_K:
		# These entries are the entries in the Configuration object:
		- 1
		- 2
		- 3
		- 7
		- 8
	# exemplary entry in the corresponding FlavourShelf 'num_K': [1, 2, 3, 7, 8]

	algorithm:
		# These entries are the entries in the Configuration object:
		- BP
		- OMP
		- ISTA
		- FISTA
		- TWISTA
	# exemplary entry in the corresponding FlavourShelf 'algorithm': ['BP', 'OMP', 'ISTA', 'FISTA', 'TWISTA']

kitchen & link
---------------

The kitchen-file is not yet used.
Further, baking many different types of pizza with different flavours might take a time if only one *worker* -- or (food-)"processor" if you like -- cooks them one after another. If you have multiple ovens or workers at your disposal, parallelization is desireable.

In the spirit of this metaphore, you might aim to scale the execution of a computation graph to multiple processor cores (or even machines in a compute cluster) easily upon availability. Therefore, everything that relates to computation resources and scheduling a cooking session.
in short, in the kitchen file you can describe the specs of the computer or system used to compute the whole recipe.


Links... link to things. :) Which will be needed later to write certain results to a paper for example.
But please ask Mr. Wagner if you aren't sure, what's meant.

recipe
------
A recipe is an immutable representation of the full compute graph of the intended operation, defining steps as the nodes of that graph and their inputs and outputs as the edges connecting them.

The definition of a recipe contains the following definitions, that usually are defined in the recipe file (see below):

	1. Mapping of a code resource to all the steps required by this recipe. These resources will always be hashed and verified during preparation of the recipe.
	2. Mapping of step input names and step output names to the recipe namespace

.. code-block::

	compute_a:
    	type: python
    	resource: steps/dosomething.py
    	inputs:
        	some_parameters: num_K
    
    	outputs:
        	result: z

	doItTwice_z:
		type: python
		resource: steps/step2.py
		inputs:
			data: z
		
		outputs:
			result: seconds

	anotherStep:
		type: python
		resource: steps/LogToLin.py
		inputs:
			data: beampatternLog
		
		outputs:
			result: beampatternLin
