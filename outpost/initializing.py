from status import set_status

def initializing(outpost_def):
    set_status("Initializing", outpost_def)
    
    print("Initializing " + outpost_def["name"])