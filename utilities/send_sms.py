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
    conn = client.HTTPSConnection("lqjgy2.api.infobip.com")
    prefix = country_code.replace("+", "")
    payload = json.dumps({
        "messages": [
            {
                "destinations": [{"to": prefix + phone_number}],
                "from": "ServiceSMS",
                "text": message
            }
        ]
    })
    headers = {
        'Authorization': 'App ab5e5e11505b02c6db662098b7c9a2d1-7d106c3e-b9ed-4698-9353-901c72cbe065',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    pass