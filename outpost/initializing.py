import os
from status import set_status

def initializing(outpost_def):
    set_status("Initializing", outpost_def)
    os.chdir(outpost_def["script_location"])
    content_dir = outpost_def["content_dir"]
    if not os.path.isdir(content_dir):
        os.makedirs(content_dir, exist_ok=True)
    print("Initializing " + outpost_def["name"])
