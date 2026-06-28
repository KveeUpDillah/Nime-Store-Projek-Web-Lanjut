import random
from django.conf import settings
from django.core.mail import send_mail

def generate_otp():

    return str(random.randint(100000,999999))

import random

from django.conf import settings

from django.core.mail import send_mail


def generate_otp():
    return str(random.randint(100000,999999))


def send_otp_email(email, otp):

    subject = "Kode OTP Anime Store"

    message = f"""

Halo,

Kode OTP Anda adalah

{otp}

Kode ini berlaku selama 5 menit.

Jangan bagikan kode ini kepada siapa pun.

Anime Store

"""

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [email],

        fail_silently=False

    )