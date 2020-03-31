# use 'make target PYTHON=/path/to/python' to specify a
# certain python version to use

# make doc: builds the sphinx docu
# make black: reformats the code
# make all: builds all of the above targets

PYTHON=python3

.PHONY: test
test: | stylecheck
	$(PYTHON) setup.py test

.PHONY: black
black:
	black -l79 chefkoch/*.py tests/*.py *.py # this is a lower case L 79

.PHONY: doc
doc:
	$(PYTHON) setup.py build_sphinx -E

.PHONY: stylecheck
stylecheck:
	pycodestyle --max-line-length=80 --statistics --ignore=E203,W503 chefkoch/*.py tests/*.py *.py

.PHONY: all
all: black test doc