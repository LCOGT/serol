from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging
from django.conf import settings

from status.models import Progress
from status.views import update_status
from notify.views import send_emails, render_email

logger = logging.getLogger(__name__)

@shared_task
def task_update_status():
    pending = Progress.objects.filter(status='Submitted')
    messages = []
    for p in pending:
        logger.debug('Checking {} for {} - PID: {}'.format(p.requestid, p.user, p.id))
        resp = update_status(user=p.user, requestid=p.requestid, token=settings.PORTAL_TOKEN)
        if resp.status_code == 200:
            message = render_email(p)
            if message:
                messages.append(message)

    logger.debug('Sending {} emails'.format(len(messages)))
    # send_emails(messages)
    return
