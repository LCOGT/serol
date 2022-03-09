from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.contrib import messages

from .forms import ContactForm

from status.models import Progress

import logging

logger = logging.getLogger(__name__)

def feedback_send(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            subject = dict(form.fields['subject'].choices)[subject]
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            plaintext = get_template('notify/feedback_message.txt')
            text_content = plaintext.render({'message': plaintext, 'email': from_email})
            try:
                send_mail(subject, message, from_email, [settings.EMAIL_COMMENTS_TO])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
                messages.success(request, 'Feedback sent')
            return redirect(reverse('home'))
    return render(request, "notify/feedback.html", {'form': form})

def successView(request):
    return HttpResponse('Success! Thank you for your message.')

def render_email(progress):
    if not progress.user.email:
        return False
    if progress.status == 'Failed':
        plaintext = get_template('notify/mail_message_failed.txt')
        subject = 'Message from Serol!'
    else:
        plaintext = get_template('notify/mail_message.txt')
        subject = 'Update from Serol!'
        htmltext = get_template('notify/mail_message.html')

    if settings.DEBUG:
        email = settings.DEMO_EMAIL
    else:
        email = progress.user.email
    data = {
                'username' : progress.user.username,
                'target'   : progress.target,
                'challenge': progress.challenge.number,
                'mission_name'  : progress.challenge.mission.name,
                'url'      : reverse('challenge',kwargs={'pk':progress.challenge.pk}),
                'image_url': progress.image_file.url,
                'BASE_URL' : settings.BASE_URL
                 }
    logger.debug("Rendering email to {} for Prog ID {}".format(progress.user.username, progress.pk))
    text_content = plaintext.render(data)
    html_content = htmltext.render(data)
    num = send_mail(subject, text_content, settings.EMAIL_FROM, [email], fail_silently=False, html_message=html_content)

    return num

def send_notifications(progress_updates):
    messages = []
    for progress in progress_updates:
        message = render_email(progress)
    logger.debug("Sent emails")
    return
