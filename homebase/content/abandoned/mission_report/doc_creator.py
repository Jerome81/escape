import paho.mqtt.client as mqtt
import json
import webbrowser
from time import sleep
from datetime import datetime
from datetime import timedelta


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
DOCUMENT_ID = "13Pzz7txy-8j__LoPIHu55LGJe_C-2miZvtY-eeqvqlw"  # https://docs.google.com/document/d/13Pzz7txy-8j__LoPIHu55LGJe_C-2miZvtY-eeqvqlw/edit?tab=t.0

# The ID of the folder into which the new doc is created
FOLDER_ID = '1ohugy5OyUwvX2D7UWaa9_8oOp8T65c6e'  # https://drive.google.com/drive/folders/1ohugy5OyUwvX2D7UWaa9_8oOp8T65c6e

mq_ip = "192.168.5.11"

deviceId = "DocWriter"

docs_service = None
doc_id = None

_jsonData = {
    "id": deviceId,
    "description": ("Keine Lösung"),
}

_language = "deutsch"
_iss_intervention = False
_score = 0

MISSION_STARTED = {
    "deutsch": "%s - Mission start",
    "english": "%s = Mission started"
}

ENTERED_SPACESHIP = {
    "deutsch": "%s - Das verlassene Raumschiff betreten",
    "english": "%s - Entered the abandoned spaceship"
}

DOCK_KEYPAD_SOLVED = {
    "deutsch": "%s - Zutrittscode geknackt",
    "english": "%s - Access code cracked"
}

DOCK_DOOR_UNLOCKED = {
    "deutsch": "%s - Dock Türe geöffnet",
    "english": "%s - Dock door opened"
}
CREW_DOOR_UNLOCKED = {
    "deutsch": "%s - Türe zum Crew Raum geöffnet",
    "english": "%s - Door to crew room opened"
}

COCKPIT_DOOR_UNLOCKED = {
    "deutsch": "%s - Türe zum Cockpit geöffnet",
    "english": "%s - Cockpit door opened"
}

INTRUDER_ALERT_SUCCESS = {
    "deutsch": "Eindringlingsalarm erfolgreich ausgeschaltet",
    "english": "Intruder alert successfully avoided"
}

INTRUDER_ALERT_FAILED = {
    "deutsch": "Eindringlingsalarm ausgelöst",
    "english": "Intruder alert triggered"
}

RIPPLIS_HINT = {
    "deutsch": "Ripplis Hilfe mit dem Dock Code benötigt",
    "english": "Needed Ripplis help with the dock code"
}

ISS_INTERVENTION = {
    "deutsch": "ISS Riddle musste das den Eindringlingsalarm ausschalten",
    "english": "ISS Riddle had to deactivate the intruder alert"
}

POWER_UP = {
    "deutsch": "Hauptstrom eingeschaltet",
    "english": "Main power activated"
}

POWER_DOWN = {
    "deutsch": "Hauptstrom ausgeschaltet...",
    "english": "Main power deactivated..."
}


QUICKNESS_BONUS = {
    "deutsch": "Geschwindigkeitsbonus",
    "english": "Bonus for speed"
}

ACCESS_GRANTED = {
    "deutsch": "%s Zugriff gewährt",
    "english": "%s Access granted"
}

ACCESS_CHECK_TRIES = {
    "deutsch": "für Fehlversuche bei der Zugriffsüberprüfung",
    "english": "for failed access check attempts"
}

NOBLE_SACRIFICE = {
    "deutsch": "Selbstzerstörung aktiviert. ISS Hofmann zerstört.",
    "english": "Self destruction activated. ISS Hofmann destroyed."
}

CORE_REMOVED = {
    "deutsch": "AI Core entfernt. Upload abgebrochen. ISS Riddle gerettet.",
    "english": "AI Core removed. Upload stopped. ISS Riddle saved."
}

MYSTERY_SOLVED = {
    "deutsch": "Funkverbindung mit Dr. Helen Rippli und Sgt. Olo aufgebaut.",
    "english": "Connection with Dr. Helen Rippli and Sgt. Olo established."
}

ANNOYED_THE_HELL_OUT_OF_THE_AI = {
    "deutsch": "Die KI geärgert, in dem ihr 10x versucht habt ins überhitzte Cockpit zu gelangen.",
    "english": "Annoyed the hell out of the AI by trying to enter the overheated cockpit 10 times."
}

INSANE = {
    "deutsch": "\"Die Definition von Wahnsinn ist, immer wieder das Gleiche zu tun und andere Ergebnisse zu erwarten.\"",
    "english": "\"Insanity is doing the same thing over and over again and expecting different results.\""
}

_start_time = None


def add_to_log(text):
    Logtag = "#LOGBUCH"
    replace_text(Logtag, text + "\n" + Logtag)


def add_score(text):
    tag = "#SCORE"
    replace_text(tag, text + "\n" + tag)


def add_to_log_with_time(text):
    print(text)
    add_to_log(text % datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

def add_to_score(score, text):
    global _score
    _score = _score + score
    add_score((text + "\t%s") % score)


# Function to replace text within a Google Doc
def replace_text(old_text, new_text):
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
    result = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    return result

def time_elapsed_in_s():
    return datetime.now() - _start_time

def on_started():
    global _start_time
    replace_text("#DATUM", datetime.today().strftime('%Y-%m-%d'))
    # Start timer
    _start_time = datetime.today()
    # Add to log
    add_to_log(MISSION_STARTED[_language] % _start_time.strftime('%Y-%m-%d %H:%M:%S'))
    add_to_log(ENTERED_SPACESHIP[_language] % (_start_time + timedelta(seconds=11)).strftime('%Y-%m-%d %H:%M:%S'))
    

def on_reset():
    # Reset timer
    pass

def on_stopped():
    # pause timer
    pass

def on_language_change(language):
    global _language
    _language = language
    print("Switching language to: %s" % language)
    text_de = "Missions-Report: Das verlassene Raumschiff"
    text_en = "Mission report: The abandoned spaceship"
    if language == "english":
        replace_text(text_de, text_en)
    if language == "deutsch":
        replace_text(text_en, text_de)

def on_event(event):
    global _intervention
    if event == "Ripplis hint":
        add_to_log_with_time(RIPPLIS_HINT[_language])
        add_to_score(-20, RIPPLIS_HINT[_language])

    if event == "ISS Riddle intervention":
        add_to_log_with_time(ISS_INTERVENTION[_language])
        add_to_score(-50, ISS_INTERVENTION[_language])
        _iss_intervention = True

    if event == "Dock door unlocked":
        add_to_log_with_time(DOCK_DOOR_UNLOCKED[_language])
        t = time_elapsed_in_s()
        if not _iss_intervention:
            add_to_score(100, INTRUDER_ALERT_SUCCESS[_language])
            if t.seconds < 180:
                add_to_score(180 - t.seconds, QUICKNESS_BONUS[_language])


    if event == "Crew door unlocked":
        add_to_log_with_time(CREW_DOOR_UNLOCKED[_language])
        add_to_score(100, CREW_DOOR_UNLOCKED[_language])

    if event == "Cockpit door unlocked":
        add_to_log_with_time(COCKPIT_DOOR_UNLOCKED[_language])
        add_to_score(100, COCKPIT_DOOR_UNLOCKED[_language])

    if event == "Dock keypad solved":
        add_to_log_with_time(DOCK_KEYPAD_SOLVED[_language])

    if event == "Power up":
        add_to_log_with_time(POWER_UP[_language])

    if event == "Power down":
        add_to_log_with_time(POWER_DOWN[_language])

    if event == "Self destruct":
        add_to_log_with_time(NOBLE_SACRIFICE[_language])
        add_to_score(400, NOBLE_SACRIFICE[_language])

    if event == "Core removed":
        add_to_log_with_time(CORE_REMOVED[_language])
        add_to_score(500, CORE_REMOVED[_language])

    if event == "Mystery solved":
        add_to_log_with_time(MYSTERY_SOLVED[_language])
        add_to_score(300, MYSTERY_SOLVED[_language])

    if event == "Access granted":
        add_to_log_with_time(ACCESS_GRANTED[_language])



                
def add_stats(payload):
    if 'Orbital' in payload:
        total_tries = payload['Orbital']
        print(total_tries)
        add_to_score((total_tries - 3) * -10, ACCESS_CHECK_TRIES[_language])
    if 'CockpitButton' in payload:
        total_button_presses = payload['CockpitButton']
        print("Total button presses: %s" % total_button_presses)
        if total_button_presses >= 10:
            add_to_score(100, ANNOYED_THE_HELL_OUT_OF_THE_AI[_language])
        else:
            if total_button_presses > 4:
                add_to_score(-25, INSANE[_language])


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
        'parents': [FOLDER_ID]  
    }
    request = service.files().copy(fileId=document_id, body=body)
    response = request.execute()
    copy_id = response.get('id')
    # to use the same doc all the time, uncomment the following line, but comment the preceding two
    #copy_id = "1Glfl9MouxVsf3KHSWUyUblfx4OhTwmCHMgJwSHPVy9A"
    print("New doc created: %s" % copy_id)
    return copy_id

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
    client.subscribe("Stats")
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
    if msg.topic == "Stats":
        add_stats(payload)
            
  
def connect(client):
    disconnected = True
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

def main():
    global docs_service
    global doc_id

    creds = login()
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    new_doc_title = 'Copied Document'

    # Copy the original document
    doc_id = "10u1GsKIHa-fthmwbpOJegzUKAUTQL7_udV85EXODlQ8" #copy_doc(drive_service, DOCUMENT_ID, new_doc_title)

    # Replace "#TEXT" with "Hello world" in the copied document
    # replace_text(docs_service, new_doc_id, 'as', 'ASS')

    print(f"Document copied successfully. New document ID: {doc_id}")
    webbrowser.open("https://docs.google.com/document/d/%s" % doc_id)
    
    while True:
        sleep(1)


    # Retrieve the documents contents from the Docs service.
#    document = service.documents().get(documentId=DOCUMENT_ID).execute()

#    print(f"The title of the document is: {document.get('title')}")



if __name__ == "__main__":
  main()

