from celery import shared_task



@shared_task
def send_otp_email(OTP_code):
    print('OTP Code is: ', OTP_code)


@shared_task
def send_link_email(link):
    print('Link is: ', link)