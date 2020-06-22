import inspect
import inspectortest

"""The following snippet returns all functionnames of inspectortest.py.
getmembers with the predicate isfunction returns all functions in a list 
of (name, value). 
"""

list = inspect.getmembers(inspectortest, predicate=inspect.isfunction)

print("Alle Funktionsnamen")
for p in list:
    print('{}'.format(p[0]))