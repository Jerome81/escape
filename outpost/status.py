from sqlitedict import SqliteDict
import requests

def send_status(status, outpost_def):
    outpost = outpost_def.copy()
    outpost["status"] = status
    response = requests.post(outpost_def["api_url"] + "outpost", json=outpost)
    response.json()

def set_status(status, outpost_def, cache_file = "status.sqlite3"):
    print("Status: " + status)
    try:
        with SqliteDict(cache_file) as outposts:
            outposts["status"] = status
            outposts.commit()
        send_status(status, outpost_def)
    except Exception as ex:
        print("Error while trying to write or send status.")
        send_status("Error while writing status: %s - Continuing")
