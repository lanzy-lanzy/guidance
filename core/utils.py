from twilio.rest import Client
from django.conf import settings

def send_appointment_sms(phone_number, message):
    """
    Send SMS notification using Twilio
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False
