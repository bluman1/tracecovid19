import json
import os
import string
import random

from app.models import Patient


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def parse_phone(phone):
    """ A valid Nigerian phone number.
    08012345678 - 11 digits starts with 0, network=80,81,70,90, followed by 8 digits
    +2348012345678 - 13 digits with +, code=234, network=80,81,70,90, followed by 8 digits
    0112345678 - 10 digits starts with 01, followed by 8 digits
    """
    network_operators = ['80', '81', '70', '90', '01']
    phone = phone.strip()
    phone = phone.replace(' ', '')
    phone = phone.replace('(', '')
    phone = phone.replace(')', '')
    phone_len = len(phone)
    if phone_len == 14 and phone.startswith('+234') and phone[4:6] in network_operators:
        # +2348012345678
        return True
    if phone_len == 11 and phone.startswith('0') and phone[1:3] in network_operators:
        # 08012345678
        return True
    if phone_len == 10 and phone.startswith('01'):
        # 0112345678
        return True
    return False


def validate_email(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def random_illustration():
    return str(random.randint(1, 22)) + '.png'

def generate_covid_id(size=8):
    chars = string.digits
    exist = True
    generated_id = ''
    while exist:
        generated_id = 'COVID-' + ''.join(random.choice(chars) for _ in range(size))
        obj_exists = Patient.objects.filter(covid_id=generated_id).exists()
        if not obj_exists:
            break
    return generated_id


def contact_chance(matched):
    """ This function calculates the chances of contact based on matched keys

    """
    probability = 0
    if 'country' in matched:
        probability += 16.6
    if 'state' in matched:
        probability += 16.7
    if 'location' in matched or 'place_id' in matched:
        probability += 16.7
    if 'date' in matched:
        probability += 16.6  # TODO: handle date_before and date_after situations
    if 'time_range' in matched:
        probability += 16.7  # TODO: handle time_range_before and time_range_after situations
    if 'activity' in matched:
        probability += 16.6  # removed 0.1 from this to get a 99.9% probability
    if 'other_activity' in matched:
        probability += 12.5
    return probability


def error_msg(msg):
    """Returns a dictionary mapping error to msg."""
    return {'status': "failed", 'message': msg}


def success_msg(msg, data):
    """Returns a dictionary mapping status, message and data."""
    return {'status': 'successful', "message": msg, 'data': data}
