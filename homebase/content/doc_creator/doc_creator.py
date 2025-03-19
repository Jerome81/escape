import paho.mqtt.client as mqtt
import json
from time import sleep


import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# https://developers.google.com/docs/api/quickstart/python?hl=de
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

# The ID of a sample document.
DOCUMENT_ID = "13Pzz7txy-8j__LoPIHu55LGJe_C-2miZvtY-eeqvqlw"

# The ID of the folder into which the new doc is created
FOLDER_ID = '1ohugy5OyUwvX2D7UWaa9_8oOp8T65c6e'

mq_ip = "192.168.178.11"

deviceId = "DocWriter"

_jsonData = {
    "id": deviceId,
    "description": ("Keine Lösung"),
}

_language = "de"

def on_started():
    # Copy document

    # Open document in Chrome

    # Fill out date
    pass

    # Start timer

def on_reset():
    # Reset timer
    pass

def on_stopped():
    # pause timer
    pass

def on_language_change(language):
    global _language
    _language = language

def on_event(event):
    pass


### Google Login ###
def login():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


# Function to copy a Google Doc
def copy_doc(service, document_id, new_title):
    body = {
        'name': "Das verlassene Raumschiff",
        'parents': [FOLDER_ID]  # You can specify a parent folder ID here
    }
    request = service.files().copy(fileId=document_id, body=body)
    response = request.execute()
    copy_id = response.get('id')
    print("New doc created: %s" % copy_id)
    return copy_id

# Function to replace text within a Google Doc
def replace_text(service, document_id, old_text, new_text):
    requests = []
    text_range = {
        'startIndex': 0,
        'endIndex': -1
    }
    match_criteria = {
        "text": old_text,
        "matchCase": True

    }
    replace_all_text = {
        'replaceAllText': {
            'contains_text': match_criteria,
            'replaceText': new_text
        }
    }
    requests.append(replace_all_text)
    result = service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return result

def find_all_text(docs_service, document_id, search_text):
    request = {
        'requests': [
            {
                'findText': {
                    'allMatches': True,
                    'matchCase': False,  # Adjust as needed
                    'text': search_text
                }
            }
        ]
    }
    response = docs_service.documents().batchUpdate(documentId=document_id, body=request).execute()
    return response['responses'][0]['findText']['matches']

### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("ToDevice/All")
    client.publish("ToHost", json.dumps(jsonData))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _gameState
    print(msg.topic)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))

    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            _gameState = payload["gameState"]
            if _gameState == "STARTED":
                on_started()
            if _gameState == "STOPPED":
                on_stopped()
            if _gameState == "RESET":
                on_reset()
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            
  
def connect(client):
    disconnected = True
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)

#mqttc = mqtt.Client()
#mqttc.on_connect = on_connect
#mqttc.on_message = on_message
#mqttc.username_pw_set(username="outpost", password="CallingHome")

#connect(mqttc)

print("starting message queue.")
#mqttc.loop_start()

def main():
    creds = login()
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    new_doc_title = 'Copied Document'

    # Copy the original document
    new_doc_id = copy_doc(drive_service, DOCUMENT_ID, new_doc_title)

    # Replace "#TEXT" with "Hello world" in the copied document
    replace_text(docs_service, new_doc_id, 'as', 'ASS')
    #for match in find_all_text(docs_service, new_doc_id, "as"):
    #    print(match["range"])

    print(f"Document copied successfully. New document ID: {new_doc_id}")




    # Retrieve the documents contents from the Docs service.
#    document = service.documents().get(documentId=DOCUMENT_ID).execute()

#    print(f"The title of the document is: {document.get('title')}")



if __name__ == "__main__":
  main()

