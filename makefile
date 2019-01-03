#
#  makefile
# ------------------------------------------------- part of the chefkoch package
#
#  makefile for assisted chefkoch package maintainance.
#
#  NOTE: when working with this file, please keep in mind that line breaks in
#        makefiles expand to one whitespace character! Deal with it. It's POSIX
#
#  Usecases:
#    - install package system-wide on your machine (needs su privileges)
#        EXAMPLE:        'make install'
#
#    - install package for your local user only (no privileges needed)
#        EXAMPLE:        'make install MODE=--user'
#
#    - compile all cython source files locally
#        EXAMPLE:        'make compile'
#
#    - debug the package by running an interactive session after compiling
#        EXAMPLE:        'make debug'
#
#    - uninstall package
#        EXAMPLE:        'make uninstall'
#        NOTE: If you have installed the package manually you need to specify
#              the MODE you have installed it with. e.g. if you installed the
#              package for your local user, you will need to specify this for
#              uninstall as well: 'make uninstall MODE=--user'. Using pip is
#              recommended though
#
#    - compile documentation with benchmarks on your machine
#        EXAMPLE:        'make doc [OPTIONS=...]'
#
#  Author      : wcw
#  Introduced  : 2019-01-03
#------------------------------------------------------------------------------
#
#  Copyright 2019 Christoph Wagner
#      https://www.tu-ilmenau.de/it-ems/
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#------------------------------------------------------------------------------

# default: Cancel with a warning as a specific target selection is required.
.PHONY: default
default: .warning

################################################################################
###  PLATFORM SPECIFIC DEFINITIONS
################################################################################

ifeq ($(OS),Windows_NT)
RM=del /F
RMR=deltree
PSEP=$(strip \)
else
RM=rm -f
RMR=rm -rf
PSEP=/
endif


################################################################################
###  LOCAL VARIABLES (user-defined in case needed)
################################################################################

# Filename for list of files installed during 'setup.py install'
FILE_LIST=setup.files

# MODE may be specified from command line for choosing install mode.

# python version
PYTHON=python

ifeq ($(OS),Windows_NT)
else

# STYLE_FILES specifies the files touched during coding style operations
STYLE_FILES=chefkoch/*.py *.py

# STYLE_IGNORES lists the errors to be skipped during style check
STYLE_IGNORES=E26,E116,E203,E221,E222,E225,E227,E241,E402,E731,W504

# TEST_OPTIONS allows passing extra options to tests during `testCode`target
TEST_OPTIONS=-i

# CODEBASE_FILES lists all source code files in codebase
CODEBASE_FILES:=$(shell find .\
		-name 'makefile' -o -name '*.tex' -o\
		-name '*.py' -o -name '*.pyx' -o -name '*.pxd'\
	| $(PYTHON) -c 'import sys; print(" ".join([s.strip()\
		for s in sys.stdin.readlines() if "output" not in s]))')
endif

################################################################################
###  BUILD TARGETS
################################################################################

# target 'install': Install package
.PHONY: install
install:
	$(info * installing ... (generating '$(FILE_LIST)'))
	$(info * using special mode: $(MODE))
	$(PYTHON) setup.py install --record $(FILE_LIST) $(MODE)


# target 'uninstall': Uninstall package
.PHONY: uninstall
uninstall: $(FILE_LIST)
	$(info * uninstalling ... (using '$(FILE_LIST)'))
ifeq ($(OS),Windows_NT)
# Windows flavour
	@for /f %%A in ($(FILE_LIST)) do del %%A
	del $(FILE_LIST)
else
# Linux flavour
	@cat $(FILE_LIST) | xargs rm -rf
	@rm -f $(FILE_LIST)
endif


# target 'compile': Comile package locally.
.PHONY: compile
compile:
	$(info * compiling package locally)
	$(PYTHON) setup.py build_ext --inplace


# target 'doc': Compile documentation
.PHONY: doc
doc: | compile
	$(info * building documentation)
	@$(PYTHON) setup.py build_doc


# target 'all': Compile everything (code, documentation and run tests)
.PHONY: all
all: | compile doc


################################################################################
###  LINUX-ONLY BUILD TARGETS
################################################################################

ifeq ($(OS),Windows_NT)
else
# target 'styleCheck': Perform a style check for all python code files
.PHONY: styleCheck
styleCheck:
	$(info * running PEP8 code style check (excluding $(STYLE_IGNORES)))
	@pycodestyle --max-line-length=80 --statistics --count\
		--ignore=$(STYLE_IGNORES) $(STYLE_FILES)


# target 'codeStats': Print statistics about the codebase
.PHONY: codeStats
codeStats:
	$(info * LOC & SIZE for source files in codebase)
	$(info * ---------------------------------------)
	@wc -l -c $(CODEBASE_FILES)
endif


################################################################################
###  INTERNAL BUILD TARGETS
################################################################################

# target 'warning': Print warning and exit.
.PHONY: .warning
.warning:
	$(info * WARNING: no makefile target specified. Abort.)
	$(info * valid targets are: install uninstall)


################################################################################
###  RESOURCE TARGETS
################################################################################

# target '$(FILE_LIST)': Generate list of installed files.
$(FILE_LIST):
	$(info need to generate file list '$@' for uninstall)
	$(MAKE) install
