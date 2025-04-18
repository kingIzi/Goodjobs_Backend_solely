import json

import requests
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def send_sms_message(phone_number, message,country_code = '+255'):
    url = f'https://mshastra.com/sendurl.aspx?user=GOODTHINGS&pwd=epu1uhmj&senderid=GOODTHINGS&mobileno={phone_number}&msgtext={message}&priority=High&CountryCode={country_code}'

    payload = {}
    headers = {
        'Cookie': 'ASP.NET_SessionId=v0pnibhsomlnzj4aitdzqemh'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 000:
        response_string = response.text
        print(response_string)
        return json.loads(response_string)
    else:
        print(response.status_code)
        response_string = response.text
        print(response_string)

        pass  # handle error case
