Work setup
===========

This section describes how to install chefkoch, if you're a developer

The pipy installation of chefkoch provides the latest version on the master-branch, 
but for developement, the installation should happen from within the project folder. 
Therefore got to the chefkoch repsitory and type: 
``pip install -e .``

To check if chefkoch works, try
``chef version``

If this does not work, but
``which chef``
returns something like home/user/.local/bin/, your linux installation might not have 
the PATH variable updated to look into the ~/.local/bin directory. 
You can add this folder to PATH by typing
``nano ~/.bashrc``
which opens the settings for your current linux user and adding the line
``export PATH=~/.local/bin:$PATH``

Save end then you can try chef version again.
The command pip install -e . also automatically installes all required python
packages by executing
``pip install -r requirements.txt``

To write the documentation and to run the tests, there are additional packages needed.
You can install them within
``pip install -U -r requirements-dev.txt``

There are two kinds of tests included in the developement process. The first are unit
tests/test cases found in the test folder. They can be run by
``make test``.
Also, there are continious integration tests, that protect the master branch from unqualified 
pushes. They run the makefile and the unit tests. The first complaint will be about code style
which you can check with
``make stylecheck``
(DO NOT FORGET TO CHECK THIS BEFORE YOU MAKE A COMMIT!)

There is a command that fixes all easy code style problems which is
``make black``

The documentation uses sphinx, which collects the documentation string from the code and
fits them into an html page. To collect the doc-strings, user
``sphinx-apidoc doc chefkoch``

To write out the collected doc-strings into the html page, use
``sphinx-build doc build/doc``

Or just use
``make doc``
Which executes both commands. :)

If you have any problems, please check in with one of the team-members.
