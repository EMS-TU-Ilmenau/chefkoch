import inspect

def aFunction(bla=123, blub='abc'):
    pass

def varnames(f):
    """
    Given a functionname f, it returns a tuple 
    ArgSpec(args, varargs, keywords, defaults),
    where args is a list of the parameter names
    """
    return inspect.getargspec(f)[0]

def fullvarnames(f):
    return inspect.getfullargspec(f)

print(varnames(aFunction))
print("erster Argumentenname: " + (varnames(aFunction)[0]))
print(fullvarnames(aFunction))