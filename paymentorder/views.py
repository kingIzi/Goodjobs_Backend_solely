import json
import logging
from datetime import timedelta, date

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from myauthentication.models import CustomUser
from paymentorder.models import Transactions
from paymentorder.serializers import TransactionSerializer
from subscription.models import Subscription, Plan

from myauthentication.validators import FetchUsersValidator

from utilities.phone_number_refactor import determine_provider
from utilities.send_sms import send_sms_message
from goodjobs.settings import AZAMPAY_CLIENT_ID, AZAMPAY_APP_NAME, AZAMPAY_SECRET_KEY, AZAMPAY_SANDBOX_CLIENT_ID, \
    AZAMPAY_SANDBOX_APP_NAME, AZAMPAY_SANDBOX_SECRET_KEY

logger = logging.getLogger('payments_log')


def azampay_mobile_checkout(token, base_url, phone_number, order_id, amount, provider, app, user_id):
    url = f"{base_url}/azampay/mno/checkout"

    payload = json.dumps({
        "accountNumber": phone_number,
        "additionalProperties": {
            "app": app,
            "user_id": user_id
        },
        "amount": amount,
        "currency": "TZS",
        "externalId": order_id,
        "provider": provider
    })
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            json_response = response.json()
            azampay_transaction_id = json_response['transactionId']
            return {"status": "success", "status_code": 200, "azampay_transaction_id": azampay_transaction_id}
        else:
            return {'status_code': 400, 'error': response.text}
    except Exception as e:
        return {"status": "error", "status_code": 400, "error": str(e)}
        return f"An error occurred: {str(e)}"


def generate_azampay_token(authenticator_url, base_url, is_sandbox):
    url = f'{authenticator_url}/AppRegistration/GenerateToken'
    if is_sandbox:
        payload = json.dumps({
            "appName": AZAMPAY_APP_NAME,
            "clientId": AZAMPAY_SANDBOX_CLIENT_ID,
            "clientSecret": AZAMPAY_SECRET_KEY
        })
    else:
        payload = json.dumps({
            "appName": AZAMPAY_APP_NAME,
            "clientId": AZAMPAY_CLIENT_ID,
            "clientSecret": AZAMPAY_SECRET_KEY
        })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            json_response = response.json()
            access_token = json_response['data']['accessToken']
            return {'access_token': access_token, 'status_code': 200}
        else:
            return {'status_code': 400, 'error': response.text}
    except Exception as e:
        return f"An error occurred: {str(e)}"


def azampay_payment(is_sandbox, phone_number, order_id, amount, provider, app, user_id):
    if is_sandbox:
        authenticator_url = 'https://authenticator-sandbox.azampay.co.tz'
        base_url = 'https://sandbox.azampay.co.tz'
    else:
        authenticator_url = 'https://authenticator.azampay.co.tz'
        base_url = 'https://checkout.azampay.co.tz'

    token_response = generate_azampay_token(authenticator_url, base_url, is_sandbox)
    if token_response['status_code'] == 200:
        mno_checkout = azampay_mobile_checkout(token_response['access_token'], base_url, phone_number, order_id, amount,
                                               provider, app, user_id)
        return mno_checkout
    else:
        return "token has issues"


def tutume_callback(user_id, order_id):
    logger.info(f'Tutume callback called {user_id}{order_id}')


@csrf_exempt
def webhook_payment_endpoint(request):
    # Read the raw request body
    request_body = request.body
    data = json.loads(request_body)
    reference = data['reference']
    order_id = data['utilityref']
    amount_paid = data['amount']
    transaction_status = data['transactionstatus']
    additional_properties = data['additionalProperties']
    if transaction_status == 'success':
        if additional_properties['app'] == "TutumeSoko":
            user_id = additional_properties['user_id']
            tutume_callback(user_id, order_id)
            return JsonResponse({'status': 'Successfully paid'}, )
        else:

            subscription = Subscription.objects.get(id=order_id)
            plan = Plan.objects.get(price=amount_paid)
            user = subscription.user
            transactions = Transactions.objects.filter(azampay_transaction_id=reference)
            for transaction in transactions:
                transaction.is_success = True
                transaction.save()

            subscription.active = True
            subscription.is_free_trial = False
            subscription.plan = plan
            today = date.today()
            subscription.end_date = today + timedelta(days=plan.duration)
            subscription.save()
            numbers = ['255788161854', '255755817871', '255719542132', '255763469504', '255789158061']
            # numbers = ['255788161854', '255755817871']
            message = f'{user.username} mwenye namba {user.phone_number} amelipia kifurushi cha {plan.name} Tzs {amount_paid}.'
            try:
                for number in numbers:
                    send_sms_message(number, message)
            except:
                pass
            return JsonResponse({'status': 'Successfully paid', 'data': data}, )
    else:
        pass


def make_payment(user_id, order_id, amount, phone_number, provider):
    user = CustomUser.objects.get(id=user_id)
    checkout_response = azampay_payment(False, phone_number, order_id, amount, provider, "GoodJobs", user_id)
    azampay_transaction_id = checkout_response['azampay_transaction_id']
    Transactions.objects.create(user=user, payment_number=phone_number, provider=provider, order_id=order_id,
                                azampay_transaction_id=azampay_transaction_id, amount=amount)

    return checkout_response


def tutume_make_payment(user_id, order_id, amount, phone_number, provider):
    checkout_response = azampay_payment(False, phone_number, order_id, amount, provider, "TutumeSoko", user_id)
    print(f'Checkout response {checkout_response}')
    return checkout_response


@csrf_exempt
def tutume_create_order(request):
    user_id = request.POST.get('user_id')
    amount = request.POST.get('amount')
    phone_number = request.POST.get('phone_number')
    provider = determine_provider(phone_number)
    order_id = request.POST.get('order_id')

    try:
        make_payment_response = tutume_make_payment(user_id, order_id, amount, phone_number, provider)
        logger.info("make_payment_response", make_payment_response)
        status_code = make_payment_response['status_code']
        if status_code == 200:
            return JsonResponse({'status': 'success', 'message': 'Pushed wallet successfully', 'status_code': 200})
        else:
            return JsonResponse({'status': 'error', "message": 'Failed to push wallet', 'status_code': 400})

    except:
        return JsonResponse({'status': 'error', "message": 'Failed to push wallet', 'status_code': 400})


@csrf_exempt
def create_subscription(request):
    user_id = request.POST.get('user_id')
    amount = request.POST.get('amount')
    phone_number = request.POST.get('phone_number')
    provider = determine_provider(phone_number)

    try:
        subscription = Subscription.objects.get(user_id=user_id)
        make_payment_response = make_payment(user_id, subscription.id, amount, phone_number, provider, )

        status_code = make_payment_response['status_code']

        if status_code == 200:

            return JsonResponse({'status': 'success', 'message': 'Pushed wallet successfully', 'status_code': 200})
        else:
            return JsonResponse({'status': 'error', "message": 'Failed to push wallet', 'status_code': 400})
    except ObjectDoesNotExist:
        current_date = timezone.now().date()
        subscription = Subscription.objects.create(user_id=user_id, plan_id=1, start_date=current_date,
                                                   end_date=current_date, )
        make_payment_response = make_payment(user_id, subscription.id, amount, phone_number, provider)

        parsed_json = json.loads(make_payment_response)

        status_code = parsed_json['code']
        if status_code == 200:

            return JsonResponse({'status': 'success', 'message': 'Pushed wallet successfully', 'status_code': 200})
        else:
            return JsonResponse({'status': 'error', "message": 'Failed to push wallet', 'status_code': 400})


@csrf_exempt
def fetch_transactions(request):
    try:
        if request.method != 'POST': raise 'NOT POST'
        form = FetchUsersValidator(request.POST)
        if not form.is_valid(): return JsonResponse({'message': form.errors},status=400)
        user_id = form.cleaned_data['user_id']

        requesting_user = CustomUser.objects.get(id=user_id)
        # Ensure the requesting user has the necessary permissions to fetch all users
        if not requesting_user.has_perm('paymentorder.view_transactions'):
            return JsonResponse(
                {'status': 'error', 'message': "You don't have permission to perform this action", 'status_code': 403},
                status=403)
        else:
            transaction = Transactions.objects.all()
            transaction_serializer = TransactionSerializer(transaction, many=True).data
            return JsonResponse(
                {'status': 'success', 'message': 'Transactions fetched  successfully',
                 'status_code': 200, 'data': list(transaction_serializer)},
                status=200)
    except: 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)
