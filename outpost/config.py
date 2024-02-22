import os
import socket
import json

def get_config():
    script_location = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(script_location + '\config.json'):
        with open(script_location + '\config.orig') as json_file:
             print("Loading original configs")
             data = json.load(json_file)
             print(data)
             data["name"] = input("Name of device: ")
             data["api_url"] = input("API URL (e.g. http://127.0.0.1:5000/)")
             with open(script_location + '\config.json', 'w') as new_file:
                 print("Writing new config file: %s" % data)
                 json.dump(data, new_file)
     
    with open(script_location + '\config.json') as json_file:
        data = json.load(json_file)
        data["IP"] = socket.gethostbyname(socket.gethostname())
        return data

    return "" #TODO: Do something better