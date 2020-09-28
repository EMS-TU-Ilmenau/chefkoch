import inspect
# import inspectortest
import importlib
import os

"""
The following snippet demonstrates how to call a function from a different
unknown python-module using inspect and importlib
"""
def inspectMembers(path):
    # getting the module namr and the file ending
    mod_name, file_ext = os.path.splitext(os.path.split(path)[-1])
    # importing the correct module
    test = importlib.__import__(mod_name)
    print(mod_name)
    # getting all functionsname occuring in this module
    list = inspect.getmembers(test, predicate=inspect.isfunction)

    print("Alle Funktionsnamen")
    found = False
    for p in list:
        # printing all names
        print('{}'.format(p[0]))
        if p[0] == "execute":
            # searching for an execute-function
            found = True

    if found:
        print("let's go mario")
        # getting the signature of the execute function
        sig = inspect.signature(test.execute)
        # test dictionary with alle values needed
        dic =   {'a': 10, 'b':20}
        # dictionary needed for the function-call
        calldic = {}
        # filling the dictionary with the specific values
        for x in sig.parameters.values():
            calldic[str(x)] = dic[str(x)]
        
        # calling the testfunction
        test.execute(**calldic)
    else:
        print("not an option")
    
inspectMembers("./inspectortest.py")