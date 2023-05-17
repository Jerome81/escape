from download import download
from initializing import initializing
from config import get_config

from sqlitedict import SqliteDict
import requests
import urllib
import time

outpost_def = get_config()

api_url = outpost_def["api_url"]
content_dir = outpost_def["content_dir"]

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

def wait_for_internet_connection():
    count = 0
    while(True):
        count = count + 1
        try:
            urllib.request.urlopen(api_url + "/outposts", timeout = 1)
            return True
        except urllib.error.URLError:
            if count == 10:
                return False
            time.sleep(2)


if wait_for_internet_connection():
    set_status("Initializing")
    initializing(outpost_def["name"], api_url)

    set_status("Downloading")
    download(outpost_def["name"], api_url, content_dir)
else:
    print("Couldn't establish connection to Earth at " + api_url)