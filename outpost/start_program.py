import os
import subprocess

def start_program(outpost_def):
    file_path = outpost_def["content_dir"] + "/outpost.py"
    print("starting program " + file_path)
    if os.path.exists(file_path):
        subprocess.Popen(['python3', '-u', file_path])     
        print("done")
    else:
        print("Nothing to start")