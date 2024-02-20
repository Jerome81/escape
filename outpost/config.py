from os.path import exists
import socket
import json

def get_config():
    
    if not exists('config.json'):
        with open('config.orig') as json_file:
             print("Loading original configs")
             data = json.load(json_file)
             print(data)
             data["name"] = input("Name of device: ")
             data["api_url"] = input("API URL (e.g. http://127.0.0.1:5000/)")
             with open('config.json', 'w') as new_file:
                 print("Writing new config file: %s" % data)
                 json.dump(data, new_file)
     
    with open('config.json') as json_file:
        data = json.load(json_file)
        data["IP"] = socket.gethostbyname(socket.gethostname())
        return data

    return "" #TODO: Do something better