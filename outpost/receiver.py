from flask import Flask, request, jsonify
from sqlitedict import SqliteDict
from download import download

receiver = Flask(__name__)

#TODO: extract to config object (together with startup.py)
api_url = "http://127.0.0.1:5000/"
content_dir = "/var/lib/outposts/"
name = "XYZ"


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
        download(name, api_url, content_dir)
        return "OK", 200
    except Exception as ex:
        print("Error downloading data:", ex)
        return 500

