# use 'make target PYTHON=/path/to/python' to specify a
# certain python version to use

# make doc: builds the sphinx docu
# make black: reformats the code
# make all: builds all of the above targets

PYTHON=python3
FILES=chefkoch/*.py bin/* tests/*.py *.py

.PHONY: test
test: | stylecheck
	$(PYTHON) setup.py test

.PHONY: black
black:
	black -l79 $(FILES)

.PHONY: doc
doc:
	$(PYTHON) setup.py build_sphinx -E

.PHONY: stylecheck
stylecheck:
	pycodestyle --max-line-length=80 --statistics --ignore=E203,W503 $(FILES)

.PHONY: all
all: black test doc
