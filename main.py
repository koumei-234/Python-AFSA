import os
working_dir = os.getcwd()
import subprocess
subprocess.call("pwd")

for i in range(10):
    subprocess.call('python fishmain.py -j fish1.json', shell=True)
