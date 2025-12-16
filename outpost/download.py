import os
import requests
import shutil

from status import set_status

def download(name, api_url, outpost_def):
    content_dir = outpost_def["content_dir"]
    set_status("Downloading " + name + " to " + content_dir, outpost_def)
    r = requests.get(api_url + "content?id=" + name) #TODO: encode name
    if r.status_code == 404:
        set_status("404 - Directory doesn't exist: %s" % name, outpost_def)
    else:
        set_status("Content received.", outpost_def)
        open(content_dir + "temp.zip", 'wb').write(r.content)
        shutil.unpack_archive(content_dir + "temp.zip", content_dir)
        set_status("Content unpacked, download complete.", outpost_def)