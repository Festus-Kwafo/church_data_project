from django.utils.html import strip_tags
import requests
import os
from dotenv import load_dotenv
from random import randint

load_dotenv()


def get_errors_from_form(forms):
    error = []
    for field, er in forms.errors.items():
        title = field.title().replace("_", " ")
        error.append(f"{title}: {strip_tags(er)}")
        return "".join(error)


def send_otp_sms(otp, phoneNumber):
    endPoint = 'https://api.mnotify.com/api/sms/quick'
    apiKey = os.environ.get('MNOTIFY_API_KEY')
    data = {
        'recipient[]': [f'{phoneNumber}'],
        'sender': 'CLC DATA',
        'message': f'Your CLC DATA One Time Password is: {otp}',
        'is_schedule': False,
        'schedule_date': ''
    }
    url = endPoint + '?key=' + apiKey
    response = requests.post(url, data)
    data = response.json()
    return data


def get_otp():
    digit = randint(100000, 999999)
    otp = '{}'.format(digit)
    return otp
