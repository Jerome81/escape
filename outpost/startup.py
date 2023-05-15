from download import download
from initializing import initializing

from sqlitedict import SqliteDict
import requests
import socket

outpost_def = {
            "name": "XYZ", 
            "type": "puzzle", 
            "IP": socket.gethostbyname(socket.gethostname())
    }

api_url = "http://127.0.0.1:5000/"
content_dir = "d:/code/content/outposts/"

def send_status(status):
    outpost = outpost_def.copy()
    outpost["status"] = status
    response = requests.post(api_url + "outpost", json=outpost)
    response.json()

def set_status(status, cache_file = "status.sqlite3"):
    print("Status: " + status)
    try:
        with SqliteDict(cache_file) as outposts:
            outposts["status"] = status
            outposts.commit()
        send_status(status)
    except Exception as ex:
        print("Error while trying to write or send status.")
        send_status("Error while writing status: %s - Continuing")


set_status("Initializing")
initializing(outpost_def["name"], api_url)

set_status("Downloading")
download(outpost_def["name"], api_url, content_dir)