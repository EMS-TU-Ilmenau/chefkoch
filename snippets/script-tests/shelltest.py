import os
import subprocess
import shlex

#script = "/home/wiebke/Arbeit/chefkoch/snippets/script-tests/first.sh"
script = "./first.sh"
subprocess.call(shlex.split(script + ' param1 param2'))
# os.system("sh " + script)