import json

import requests
from django.views.decorators.csrf import csrf_exempt
from http import client
import json


# @csrf_exempt
# def send_sms_message(phone_number, message,country_code = '+255'):
#     print(phone_number)
#     url = f'https://mshastra.com/sendurl.aspx?user=GOODTHINGS&pwd=epu1uhmj&senderid=GOODTHINGS&mobileno={phone_number}&msgtext={message}&priority=High&CountryCode={country_code}'

#     payload = {}
#     headers = {
#         'Cookie': 'ASP.NET_SessionId=v0pnibhsomlnzj4aitdzqemh'
#     }

#     response = requests.request("GET", url, headers=headers, data=payload)

#     if response.status_code == 000:
#         response_string = response.text
#         print(response_string)
#         return json.loads(response_string)
#     else:
#         print(response.status_code)
#         response_string = response.text
#         print(response_string)

#         pass  # handle error case

@csrf_exempt
def send_sms_message(phone_number, message,country_code = '+255'): 
    url = 'https://apisms.beem.africa/v1/send'
    payload = {
        "source_addr": "GOODJOBS",
        "schedule_time": "",
        "encoding": "0",
        "message": message,
        "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": f'{country_code[1:]}{phone_number}'
                }
            ]
    }
    username = '102dbd7cdedacf4d'
    password = 'YTQ1MWNhMmE0NWU4YjdlOWQ5ODM0ZTljNzdhMzc3NjBhOGYzNDdhNzhjMTY3YTkwMTYyZDQ2NGRjNjRkM2I3MA'
    response = requests.request("POST", url, json=payload, auth=(username,password))
    if response.status_code == 200:
        return response.json()


@csrf_exempt
def send_sms_email(email, message): 
    send_email_url = 'https://mandombe-api.vercel.app/send-email'
    params = {
        'fullName': 'GOODJOBS',
        'message': message,
        'email': email
    }
    headers = {
        "Content-Type": "application/json"
    }
    #response = requests.post(send_email_url,headers=headers,json=payload)
    response = requests.get(send_email_url, params=params,headers=headers)
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text) 