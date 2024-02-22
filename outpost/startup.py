from download import download
from initializing import initializing
from config import get_config
from start_server import start_server
from start_program import start_program

from sqlitedict import SqliteDict
import requests
import urllib
import time
import socket


outpost_def = get_config()

api_url = outpost_def["api_url"]
content_dir = outpost_def["content_dir"]


def wait_for_internet_connection():
    count = 0
    while(True):
        count = count + 1
        try:
            urllib.request.urlopen(api_url + "/outposts", timeout = 1)
            return True
        except urllib.error.URLError:
            if count == 10:
                print("Connection to homebase failed. Using local version.")
                return False
            time.sleep(2)

initializing(outpost_def)
if wait_for_internet_connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    outpost_def["IP"] = s.getsockname()[0] # socket.gethostbyname(socket.gethostname())
    download(outpost_def["name"], api_url, outpost_def)
else:
    print("Couldn't establish connection to Homebase at " + api_url)

start_server(outpost_def)
start_program(outpost_def)
while(True):
    time.sleep(2)
    print("Alive")