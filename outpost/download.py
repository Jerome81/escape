import requests
import shutil

def download(name, api_url, content_dir):
    print("Downloading " + name + " to " + content_dir)
    r = requests.get(api_url + "content?id=" + name) #TODO: encode name
    open(content_dir + "temp.zip", 'wb').write(r.content)
    shutil.unpack_archive(content_dir + "temp.zip", content_dir)