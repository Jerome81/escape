import requests
import socket
import time
import urllib

cache = {} 
cache["ip_address"] = None
cache["spaceship_address"] = "http://localhost:5002"

def wait_for_internet_connection():
    count = 0
    while(True):
        count = count + 1
        try:
            urllib.request.urlopen(cache["spaceship_address"] + "/status", timeout = 1)
            return True
        except urllib.error.URLError:
            if count == 10:
                print("Connection to homebase failed. Using local version.")
                return False
            time.sleep(2)


def get_ip_address():
    if wait_for_internet_connection():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0] # socket.gethostbyname(socket.gethostname())
    else:
        print("Couldn't establish connection to Homebase at " + cache["spaceship_address"])


def send_status(module, status, port):
    if cache["ip_address"] is None:
        cache["ip_address"] = get_ip_address() + ":" + port
    
    response = requests.get(cache["spaceship_address"] +"/module/" + module + "/" + cache["ip_address"] + "/" + status)
    print(response)
    #response.json()

