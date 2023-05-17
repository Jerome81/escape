import socket

def get_config():
    return {
            "name": "puck_man", 
            "type": "display", 
            "IP": socket.gethostbyname(socket.gethostname()),
            "api_url": "http://127.0.0.1:5000/",
            "content_dir": "/var/lib/outposts/"
    }