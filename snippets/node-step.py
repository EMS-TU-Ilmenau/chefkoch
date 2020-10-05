class Node:
    """
    A node encapsules a simulation step within a recipe. The step can
    be realised by a python file, a sub-recipe or a built-in function.
    Each node also has a name, a dict of inputs and a dict of outputs.
    To the inputdict, the key is the same input name that the step takes,
    the value is where the input comes from. To the outputdict, the key
    is the name the step uses, the value is the name under which the
    output is available to other nodes in the recipe (the same name used
    as value in another inputdict).
    """

    def __init__(self, name, inputdict, outputdict, stepsource, steptype):
        """
        Initializes a node of the recipe. A node represents a simulation
        step.

        Parameters
        ----------
        name (str):
            Name of the simulation step.
        inputdict (dict):
            Dictionary of all inputs needed to execute this step.
        outputdict (dict):
            Dictionary of all outputs of the simulation step.
        stepsource (str):
            Information on how to execute this step.

        Raises
        ------
        TypeError:
            If the input or output of a node are not given as a dict.
        """
        # for empty name enter "" into recipe
        # unicode and string needed
        try:
            name_obj = Name(name)
            self.name = name_obj.name  # Willi, ist das wirklich so gemeint?
        except TypeError as err:
            pass
        # testing the input to be delivered in a dict
        if not (isinstance(inputdict, dict)):
            raise TypeError(
                "The input of node "
                + str(name)
                + ' must be of the format {"name as in'
                + ' step": value, ...}'
            )
            return
        self.inputs = inputdict
        # later replace strings by values in flavour?
        # testing the output to be delivered in a dict
        if not (type(outputdict) == dict):
            raise TypeError(
                "The output of node "
                + str(name)
                + ' must be of the format {"name as in '
                + 'step": value, ...}'
            )
            return
        self.outputs = outputdict
        # hier müssen vllt mehr Parameter übergeben werden
        # fehlt wahrscheinlich noch der entsprechende shelf
        # genaue Einsortierung in shelves nochmal besprechen
        # wir brauchen hier irgenwie die konkreten shelves
        # müssen hier irgendwie richtig übergeben werden
        # test ob wir die korrekt übergeben können
        rightStep(steptype)
        # todo abort in higher level and ignore whole node
    
    def rightStep(self, steptype):
        """
        defining the right step

        Parameters
        ----------
        stepsource(str):
            filepath to the source
        """
        # missing some options
        if steptype == "python":
            self.step = StepPython(self, stepsource)
        elif steptype == "shell":
            self.step = StepShell(stepsource)
        # elif extension == ".json":
        #     self.step = StepSubRecipe(stepsource)
        else:
            raise TypeError(
                "Stepsource : "
                + str(stepsource)
                + " we don't support this format."
            )

class StepResource:
    """
    Specifies the function to be executed inside a node in the recipe.
    """

    @abstractmethod
    def __init__(self, stepsource):
        """
        tests if the file exists

        Parameters
        ----------
        stepsource (str):
            filepath to recipe

        Raises
        ------
        Error: einen directory-Fehler
            
        """
        # we need the correct path, would be the path from chef + steps
        # whatever is written as name
        # should there be a connection for resource and resourcestep?
        # or is it just a to verify the code, in this case it would probably
        # more appropriate to keep it there, so you can check with a hash for changes
