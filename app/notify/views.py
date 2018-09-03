from django.shortcuts import render
from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse

from status.models import Progress

import logging

logger = logging.getLogger(__name__)

def render_email(progress):
    if not progress.user.email:
        return False
    if progress.status == 'Failed':
        plaintext = get_template('notify/mail_message_failed.txt')
        subject = 'Message from Serol!'
    else:
        plaintext = get_template('notify/mail_message.txt')
        subject = 'Update from Serol!'

    if settings.DEBUG:
        email = settings.DEMO_EMAIL
    else:
        email = progress.user.email
    data = {
                'username' : progress.user.username,
                'target'   : progress.target,
                'challenge': progress.challenge.number,
                'mission'  : progress.challenge.mission.number,
                'url'      : reverse('challenge',kwargs={'pk':progress.challenge.pk})
                 }
    logger.debug("Rendering email to {} for Prog ID {}".format(progress.user.username, progress.pk))
    text_content = plaintext.render(data)
    message = (subject, text_content, settings.EMAIL_FROM, [email])
    return message

def send_notifications(progress_updates):
    messages = []
    for progress in progress_updates:
        message = render_email(progress)
        messages.append(message)
    logger.debug("Sending {} emails".format(len(messages)))
    send_mass_mail(messages, fail_silently=False)
    return
