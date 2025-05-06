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
    #conn = client.HTTPSConnection("lqjgy2.api.infobip.com")
    conn = client.HTTPSConnection("4eze58.api.infobip.com")
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
        #'Authorization': 'App ab5e5e11505b02c6db662098b7c9a2d1-7d106c3e-b9ed-4698-9353-901c72cbe065',
        'Authorization': 'App 6c08acc93799e1855ab66ca010f5fd57-d333325d-87b3-486c-a780-5c6f90590af3',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    pass


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