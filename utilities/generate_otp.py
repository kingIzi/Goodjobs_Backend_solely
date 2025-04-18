import math
import random

from django.utils import timezone

from myauthentication.models import OTP
from django.utils import timezone

def can_generate_otp(phone_number):
    """
    determines if number is eligible for an otp renew 

    Args:
        phone_number (str): The user's phone number

    Returns:
        bool: True if number does not exist or last_request < today.
    """
    try:
        otp_record = OTP.objects.get(phone_number=phone_number)
        today = timezone.now().date()
        if otp_record.is_verified and otp_record.last_requested == today:
            return False
        elif otp_record.request_count >= 3 and otp_record.last_requested == today:
            return False
        elif otp_record.last_requested < today:
            otp_record.request_count = 0  # Reset count for a new day
            otp_record.last_requested = today
            otp_record.save()
            return True
        else:
            return True


    except OTP.DoesNotExist:
        return True  # No record exists, can generate OTP


def create_or_update_otp(first_name, last_name, email, phone_number, otp_value):
    """
    Updates an OTP entry for a given phone number with a new OTP value,
    handling the request_count correctly.
    """
    otp_record, created = OTP.objects.get_or_create(
        phone_number=phone_number,
        defaults={'otp_value': otp_value, 'request_count': 1, 'last_requested': timezone.now().date(), 'first_name': first_name, 'last_name': last_name, 'email': email}
    )
    if not created:
        if otp_record.last_requested < timezone.now().date():
            otp_record.request_count = 1  # Reset count for a new day
        else:
            # Increment only if it's the same day and not resetting after verification
            otp_record.request_count += 1
        otp_record.otp_value = otp_value
        otp_record.first_name = first_name
        otp_record.last_name = last_name
        otp_record.email = email,
        otp_record.last_requested = timezone.now().date()
        otp_record.save()


def generateOTP(password_length = 4):
    """
    Generates random string from digits 0123456789
    Args:
        password_length (int): Length of string

    Returns:
        str: Password code
    """
    digits = "0123456789"
    return "".join([ digits[math.floor(random.random() * len(digits))] for _ in range(password_length) ])

