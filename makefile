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
<<<<<<< HEAD
	black -l79 chefkoch/*.py tests/*.py *.py # this is a lower case L 79
=======
	black -l79 $(FILES)
>>>>>>> 6bd14a202e4f8b7ae77b46144d2fa1bf0ec7e345

.PHONY: doc
doc:
	$(PYTHON) setup.py build_sphinx -E

.PHONY: stylecheck
stylecheck:
<<<<<<< HEAD
	pycodestyle --max-line-length=80 --statistics --ignore=E203,W503 chefkoch/*.py tests/*.py *.py
=======
	pycodestyle --max-line-length=80 --statistics --ignore=E203,W503 $(FILES)
>>>>>>> 6bd14a202e4f8b7ae77b46144d2fa1bf0ec7e345

.PHONY: all
all: black test doc
