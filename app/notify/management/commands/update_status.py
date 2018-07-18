from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from status.models import Progress
from status.views import update_status
from notify.views import send_emails, render_email

class Command(BaseCommand):
    help = 'Update status of submitted observations'

    def handle(self, *args, **options):
        pending = Progress.objects.filter(status='Submitted')
        messages = []
        for p in pending:
            self.stdout.write('Checking {} for {} - PID: {}'.format(p.requestid, p.user, p.id))
            resp = update_status(p.user, p.requestid, token=settings.PORTAL_TOKEN)
            if resp.status_code == 200:
                message = render_email(p)
                if message:
                    messages.append(message)
                # Create an image with our pipeline
                img_resp = make_image(p)
                self.stdout.write('Image for {}: {}'.format(p.id, img_resp))

        self.stdout.write('Sending {} emails'.format(len(messages)))
        send_emails(messages)
