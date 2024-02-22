import os

from flask import Flask, request, jsonify
from sqlitedict import SqliteDict
from download import download
from config import get_config

receiver = Flask(__name__)

outpost_def = get_config()

api_url = outpost_def["api_url"]
content_dir = outpost_def["content_dir"]
name = outpost_def["name"]


@receiver.get("/state")
def get_state(cache_file = "status.sqlite3"):
    try:
        with SqliteDict(cache_file) as outpost:
            value = outpost["status"] 
            print(value)
        return value
    except Exception as ex:
        print("Error loading data:", ex)
        return 500

@receiver.get("/download")
def get_download():
    try:
        download(name, api_url, outpost_def)
        return "OK", 200
    except Exception as ex:
        print("Error downloading data:", ex)
        return 500

@receiver.get("/reboot")
def reboot():
    if request.args["pwd"] == "why_not":
        os.system('sudo shutdown -r now')
        return "OK", 200
    else:
        return 404
