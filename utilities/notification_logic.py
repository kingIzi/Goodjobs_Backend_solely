import json
import os
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials
from firebase_admin.messaging import UnregisteredError

from firebaseapp.models import FirebaseApp


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# creds = {
# }

creds = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../serviceAccountKey.json")

cred = credentials.Certificate(creds)
firebase_admin.initialize_app(cred)


def dummydata():
    data = {
        "token": "dNdXstzrTa-MCq9htYbSlj:APA91bEmHzSY_j1qCLw5yP5qk27K7Lj62PG8Sku2ZjPi1MAUbf1d-g1ABIj1qkZL0zyxYxPCiZVGg5OwSFbZTzgViXAfT1lTSSW9bzhmnCvvEGeUWMzHB3lc3DhG2ze18C845TRLvbnd",
        "intent": "",
        "title": "",
        "body": ""
    }

    return create_user_notification(data)


def create_match_notification(title, body):
    data = {
        "token": "dNdXstzrTa-MCq9htYbSlj:APA91bEmHzSY_j1qCLw5yP5qk27K7Lj62PG8Sku2ZjPi1MAUbf1d-g1ABIj1qkZL0zyxYxPCiZVGg5OwSFbZTzgViXAfT1lTSSW9bzhmnCvvEGeUWMzHB3lc3DhG2ze18C845TRLvbnd",
        "intent": "match",
        "title": title,
        "body": body,
        "topic": "all"
    }
    create_group_notification(data)


def create_user_notification(data):
    try:

        message = messaging.Message(
            notification=messaging.Notification(
                title=data['title'],
                body=data['body'],
            ),
            data=data,

            token=data['token']
        )
        if data['token']:
            response = messaging.send(message)
        else:
            response = ""
    except UnregisteredError as e:
        response = {'code': 300, "msg": str(e)}

    return json.dumps(response)


def create_group_notification(data):
    data['click_action'] = "FLUTTER_NOTIFICATION_CLICK"
    data['sound'] = "default"
    data['status'] = "done"

    try:

        message = messaging.Message(
            notification=messaging.Notification(
                title=data['title'],
                body=data['body'],
            ),

            data=data,
            topic=data['topic']

        )
        if data['token']:
            response = messaging.send(message)
        else:
            response = ""
    except UnregisteredError as e:
        response = {'code': 300, "msg": str(e)}

    return json.dumps(response)

