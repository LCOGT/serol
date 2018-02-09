from django.shortcuts import render
from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import get_template

def render_email(progress):
    if not progress.user.email:
        return False
    plaintext = get_template('notify/mail_message.txt')
    subject = 'Update from Serol!'
    data = {
                'username' : progress.user.username,
                'target'   : progress.target,
                'challenge': progress.challenge.number,
                'mission'  : progress.challenge.mission.number
                 }
    text_content = plaintext.render(data)
    message = (subject, text_content, settings.EMAIL_FROM, [progress.user.email])
    return message

def send_emails(messages):
    send_mass_mail(messages, fail_silently=False)
    return
