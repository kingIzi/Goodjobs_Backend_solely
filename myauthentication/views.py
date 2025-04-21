from rx import operators as ops, from_ as rxFrom,just
from datetime import datetime, timedelta

from myauthentication.models import CustomUser
from django.http import JsonResponse, HttpResponse
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.core.mail import BadHeaderError


from subscription.models import Subscription, Plan
from .models import CustomUser as User
from utilities.send_sms import send_sms_message
from .models import OTP
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from utilities.generate_otp import generateOTP, can_generate_otp, create_or_update_otp
from .serializers import UserSerializer

from myauthentication.validators import SignUpForm,VerifySignUpOtpForm,LoginValidator,VerifyLoginOtpForm,FetchUsersValidator,ResendOtpForm


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret

@csrf_exempt
def resend_otp_code(request):
    try:
        if request.method == 'POST':
            form = ResendOtpForm(request.POST)
            if not form.is_valid():
                return JsonResponse({'message': form.errors},status=400)
            phone_number = f"0{form.cleaned_data['phone_number']}"
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                if can_generate_otp(phone_number):  
                    otp_value = generateOTP()  
                    create_or_update_otp(user.first_name, user.last_name, user.email, phone_number, otp_value)  # Update or create the OTP entry
                    message = f'Weka token ili kuendelea. Token yako ni {otp_value}'
                    # send = just(phone_number)
                    # send.subscribe(
                    #     lambda _: send_sms_message(phone_number, message),
                    #     on_error = lambda e: print("Error : {0}".format(e)),
                    #     on_completed = lambda: print("Job Done!")
                    # )
                    return JsonResponse({'status': 'success', 'message': 'please input otp to complete authentication',
                                        'status_code': 201}, status=200)
                else:
                    return JsonResponse(
                        {'status': 'error', 'message': "OTP request limit reached. Please try again after 24 hours.",
                        'status_code': 429},
                        status=429)
            except:
                return JsonResponse({'status': 'error', 'message': "This phone number does not exists. Create a new account or check your sms", 'status_code': 404, },
                            status=404)
    except:
        return JsonResponse({'status': 'An error occurred on the server'},status=500)

# Sign up user
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'message': form.errors},status=400)

        phone_number = f"0{form.cleaned_data['phone_number']}"
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']

        if CustomUser.objects.filter(phone_number=phone_number).first():
            return JsonResponse({'status': 'error', 'message': "This number already exists", 'status_code': 400},
                                status=400)
        if CustomUser.objects.filter(username=request.POST.get('username')).first():
            return JsonResponse({'status': 'error', 'message': "This username already exists", 'status_code': 400},
                                status=400)
        if CustomUser.objects.filter(email=request.POST.get('email')).first():
            return JsonResponse({'status': 'error', 'message': "This email already exists", 'status_code': 400},
                                status=400)
        try:
            if can_generate_otp(phone_number):  
                otp_value = generateOTP()  
                create_or_update_otp(first_name, last_name, email, phone_number, otp_value)  # Update or create the OTP entry
                message = f'Weka token ili kuendelea. Token yako ni {otp_value}'
                send_sms_message(phone_number, message)  # Your existing function to send the OTP
                return JsonResponse({'status': 'success', 'message': 'please input otp to complete authentication',
                                     'status_code': 201}, status=200)
            else:
                return JsonResponse(
                    {'status': 'error', 'message': "OTP request limit reached. Please try again after 24 hours.",
                     'status_code': 429},
                    status=429)
        except:
            return JsonResponse(
                {'status': 'error', 'message': 'Error creating user. Please try again soon', 'status_code': 400},
                status=400)
    else:
        return JsonResponse({'status': 'not POST'})


# verify user signup OTP
@csrf_exempt
def verify_signup_otp(request):
    try:
        if request.method != 'POST': 
            raise 'Not POST'
        
        form = VerifySignUpOtpForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'message': form.errors},status=400)
        
        phone_number = f"0{form.cleaned_data['phone_number']}"
        otp_value = form.cleaned_data['otp_value']
        current_otp = OTP.objects.filter(phone_number=phone_number, otp_value=otp_value)
        print(f"Phone number: {phone_number}, OTP value: {otp_value}")
        if current_otp.exists():
            # user_tuple = CustomUser.objects.filter(phone_number=phone_number)[0]
            # token = Token.objects.create(user=user_tuple) 
            # plan = Plan.objects.filter(name='Free')
            # Subscription.objects.get_or_create(user=user_tuple, plan=plan[0], 
            #                                    end_date=datetime.now().date() + timedelta(days=3),
            #                                    active=True, is_free_trial=True)
            # rxFrom(OTP.objects.filter(phone_number=phone_number)).subscribe(on_next=lambda otp: otp.delete())
            # return JsonResponse({'status': 'success', 'message': 'User created successfully', 'token': str(token),
            #                      'first_name': user_tuple.first_name, 'user_id': user_tuple.id,
            #                      'phone_number': user_tuple.phone_number,
            #                      'status_code': 201}, status=201)
            return JsonResponse({'status': 'error', 'message': "Yango oyo", 'status_code': 200, }, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': "Invalid verification code", 'status_code': 404, }, status=404)
        # if current_otp.exists():
        #     user_tuple = CustomUser.objects.filter(phone_number=phone_number)[0]
        #     token = Token.objects.create(user=user_tuple) 
        #     plan = Plan.objects.filter(name='Free')
        #     Subscription.objects.get_or_create(user=user_tuple, plan=plan[0], 
        #                                        end_date=datetime.now().date() + timedelta(days=3),
        #                                        active=True, is_free_trial=True)
        #     rxFrom(OTP.objects.filter(phone_number=phone_number)).subscribe(on_next=lambda otp: otp.delete())
        #     return JsonResponse({'status': 'success', 'message': 'User created successfully', 'token': str(token),
        #                          'first_name': user_tuple.first_name, 'user_id': user_tuple.id,
        #                          'phone_number': user_tuple.phone_number,
        #                          'status_code': 201}, status=201)
        # else:
        #     return JsonResponse({'status': 'error', 'message': "Invalid verification code", 'status_code': 404, }, status=404)
    except:
        return JsonResponse({'status': 'An error occurred on the server'},status=500)

# verify user login OTP
@csrf_exempt
def verify_login_otp(request):
    try:
        if request.method != 'POST':
            raise 'NOT POST'
        form = VerifyLoginOtpForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'message': form.errors},status=400)
        phone_number = f"0{form.cleaned_data['phone_number']}"
        otp_value = form.cleaned_data['otp_value']
        current_otp = OTP.objects.filter(phone_number=phone_number, otp_value=otp_value)
        if not current_otp.exists():
            return JsonResponse({'status': 'error', 'message': "Invalid verification code", 'status_code': 404, }, status=404)
        current_user = CustomUser.objects.get(phone_number=phone_number)
        token = Token.objects.get(user=current_user)
        rxFrom(OTP.objects.filter(phone_number=phone_number)).subscribe(on_next=lambda otp: otp.delete())
        return JsonResponse({'status': 'success', 'message': 'Success, welcome back', 'token': str(token),
                                     'first_name': str(current_user.first_name), 'user_id': str(current_user.id),
                                     'phone_number': str(current_user.phone_number),
                                     'user_image': str(current_user.user_image),
                                     'username': current_user.username,
                                     'status_code': 200}, status=200)
    except:
        return JsonResponse({'status': 'An error occurred on the server'},status=500)


# Login user

@csrf_exempt
def login(request):
    try:
        if request.method != 'POST': 
            raise 'Not POST'
        
        form = LoginValidator(request.POST)
        if not form.is_valid():
            return JsonResponse({'message': form.errors,'status': 'error','status_code': 400},status=400)
        
        status = form.cleaned_data['status']
        phone_number = f"0{form.cleaned_data['phone_number']}"
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except:
            return JsonResponse({'status': 'error', 'message': "This phone number does not exists. Create a new account or check your sms", 'status_code': 404, },
                        status=404)

        if status == 'staff' and user.is_staff:
            #otp_value = generateOTP()
            #create_or_update_otp('', '', '', phone_number, otp_value)
            #message = f'Weka token ili kuendelea. Token yako ni {otp_value}'
            #send_sms_message(phone_number, message)
            return JsonResponse({'status': 'success', 'message': 'Please input otp to complete authentication',
                                        'status_code': 200}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': "You are not authorized to login to this platform. STAFF ONLY", 'status_code': 404, },
                                        status=404)
    except:
        return JsonResponse({'status': 'An error occurred on the server'},status=500)


# Change current password
@csrf_exempt
def change_current_password(request):
    if request.method == 'POST':
        user = authenticate(request, phone_number=request.POST.get('phone_number'),
                            password=request.POST.get('current_password'))
        if user is None:
            return JsonResponse(
                {'status': 'error', 'message': 'incorrect password reset password if you dont remember',
                 'status_code': 400},
                status=400)
        else:
            user.set_password(request.POST.get('new_password'))
            user.save()
            token = Token.objects.filter(user=user)
            new_key = token[0].generate_key()
            token.update(key=new_key)
            new_token = Token.objects.get(user=user)
            return JsonResponse(
                {'status': 'success', 'message': 'Password changed successfully', 'token': str(new_token),
                 'username': str(user.username), 'user_id': str(user.id), 'status_code': 200},
                status=200)


# Forget password
@csrf_exempt
def forget_password_send_0TP(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).first():
            verification_code = generateOTP()
            user = CustomUser.objects.get(phone_number=phone_number)
            if OTP.objects.filter(user=user).exists():
                current_otp = OTP.objects.filter(user=user)
                for available_otp in current_otp:
                    available_otp.delete()

            otp_model = OTP()

            otp_model.user = user
            otp_model.otp_value = verification_code
            otp_model.save()

            message = f'Weka token ili kuendelea. Token yako ni  {verification_code}'
            try:
                send_sms_message(phone_number, message)
                return JsonResponse({'status': 'success', 'message': 'Password reset sent successfully check your sms',
                                     'status_code': 200}, status=200)

            except BadHeaderError:
                return HttpResponse('Invalid Header.')
        else:
            return JsonResponse(
                {'status': 'error', 'message': "This phone number doesn't exists", 'status_code': 404, },
                status=404)


# Verify user email
@csrf_exempt
def verify_user_send_OTP(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).first():
            verification_code = generateOTP()
            user = CustomUser.objects.get(phone_number=phone_number)
            if OTP.objects.filter(user=user).exists():
                current_otp = OTP.objects.filter(user=user)
                for available_otp in current_otp:
                    available_otp.delete()

            otp_model = OTP()

            otp_model.user = user
            otp_model.otp_value = verification_code
            otp_model.save()
            user_phone_number = user.phone_number
            print(user_phone_number)
            message = f'Weka token ili kuendelea. Token yako ni  {verification_code}'
            try:
                send_sms_message(user_phone_number, message)
                return JsonResponse(
                    {'status': 'success', 'message': 'verification code sent successfully check your sms',
                     'status_code': 200, 'otp': verification_code},
                    status=200)

            except BadHeaderError:
                return HttpResponse('Invalid Header.')
        else:
            return JsonResponse(
                {'status': 'error', 'message': "This phone number doesn't exists", 'status_code': 404, },
                status=404)


# Verify user email
@csrf_exempt
def verify_user_send_OTP(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).first():
            verification_code = generateOTP()
            user = CustomUser.objects.get(phone_number=phone_number)
            if OTP.objects.filter(user=user).exists():
                current_otp = OTP.objects.filter(user=user)
                for available_otp in current_otp:
                    available_otp.delete()

            otp_model = OTP()

            otp_model.user = user
            otp_model.otp_value = verification_code
            otp_model.save()
            user_phone_number = user.phone_number
            print(user_phone_number)
            message = f'Weka token ili kuendelea. Token yako ni  {verification_code}'
            try:
                send_sms_message(user_phone_number, message)
                return JsonResponse(
                    {'status': 'success', 'message': 'verification code sent successfully check your sms',
                     'status_code': 200, 'otp': verification_code},
                    status=200)

            except BadHeaderError:
                return HttpResponse('Invalid Header.')
        else:
            return JsonResponse(
                {'status': 'error', 'message': "This phone number doesn't exists", 'status_code': 404, },
                status=404)


# Verify forget password otp
@csrf_exempt
def verify_forget_password_otp(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(phone_number=request.POST.get('phone_number'))
        if OTP.objects.filter(user=user, otp_value=request.POST.get('otp_value')).exists():
            current_otp = OTP.objects.filter(user=user)
            for available_otp in current_otp:
                available_otp.delete()
            return JsonResponse(
                {'status': 'success', 'message': 'verification code verified successfully',
                 'status_code': 200},
                status=200)

        else:
            return JsonResponse({'status': 'error', 'message': "Invalid verification code ", 'status_code': 404, },
                                status=404)


# Change forget password
@csrf_exempt
def change_forget_password(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user = CustomUser.objects.get(phone_number=phone_number)
        user.set_password(request.POST.get('new_password'))
        user.save()
        token = Token.objects.filter(user=user)
        new_key = token[0].generate_key()
        token.update(key=new_key)
        new_token = Token.objects.get(user=user)
        return JsonResponse(
            {'status': 'success', 'message': 'Password changed successfully', 'token': str(new_token),
             'username': str(user.username), 'user_id': str(user.id), 'status_code': 200},
            status=200)


@csrf_exempt
def delete_user_data(request):
    user_id = request.POST.get('user_id')
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        # Any additional cleanup or related data deletion can be performed here
        return JsonResponse(
            {'status': 'success', 'message': 'Account Deleted successfully', 'status_code': 200},
            status=200)
    except User.DoesNotExist:
        # Handle case when the user doesn't exist
        return JsonResponse({'status': 'error', 'message': "User doesn't exist ", 'status_code': 404, },
                            status=404)


@csrf_exempt
def pull_user_details(request):
    user_id = request.POST.get('user_id')
    try:
        user = CustomUser.objects.get(id=user_id)
        user_serializer = UserSerializer(user, many=False).data
        # Any additional cleanup or related data deletion can be performed here
        return JsonResponse(
            {'status': 'success', 'message': 'User Pulled Successfully', 'data': user_serializer, 'status_code': 200},
            status=200)
    except User.DoesNotExist:
        # Handle case when the user doesn't exist
        return JsonResponse({'status': 'error', 'message': "User doesn't exist ", 'status_code': 404, },
                            status=404)


@csrf_exempt
def update_user_profile(request):
    user_id = request.POST.get('user_id')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')

    user_image = request.FILES.get('user_image')
    try:
        user = CustomUser.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Update the user's image only if an image is provided
        if user_image is not None:
            user.user_image = user_image

        user.save()

        user_serializer = UserSerializer(user, many=False).data
        return JsonResponse(
            {'status': 'success', 'message': 'Updated User Successfully', 'data': user_serializer, 'status_code': 200},
            status=200)
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': "User not found", 'status_code': 404}, status=404)
    except Exception as e:
        # It's generally a good idea to log the exception to understand what went wrong
        return JsonResponse(
            {'status': 'error', 'message': "Problem updating profile please try again later", 'status_code': 500,
             'error': str(e)},
            status=500)


@csrf_exempt
def fetch_users(request):
    try:
        if request.method != "POST": raise "NOT POST"
        #user_id = request.POST.get('user_id')
        form = FetchUsersValidator(request.POST)
        if not form.is_valid(): return JsonResponse({'message': form.errors},status=400)
        user_id = form.cleaned_data['user_id']
        
        requesting_user = CustomUser.objects.get(id=user_id)
        # Ensure the requesting user has the necessary permissions to fetch all users
        if not requesting_user.has_perm('myauthentication.view_customuser'):
            return JsonResponse(
                {'status': 'error', 'message': "You don't have permission to perform this action", 'status_code': 403},
                status=403)
        else:

            user = CustomUser.objects.all()

            user_serializer = UserSerializer(user, many=True).data
            # Any additional cleanup or related data deletion can be performed here
            return JsonResponse(
                {'status': 'success', 'message': 'User Pulled Successfully', 'data': list(user_serializer), 'status_code': 200},
                status=200)
    except: 
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'status_code': 400}, status=400)



