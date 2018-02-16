from django.core.management.base import BaseCommand, CommandError

from status.models import Progress
from status.views import update_status
from notify.views import send_emails, render_email

class Command(BaseCommand):
    help = 'Update status of submitted observations'

    def handle(self, *args, **options):
        pending = Progress.objects.filter(status='Submitted')
        messages = []
        for p in pending:
            self.stdout.write('Checking {}'.format(p.requestid))
            resp = update_status(p.user, p.requestid)
            if resp.status_code == 200:
                message = render_email(p)
                if message:
                    messages.append(message)

        self.stdout.write('Sending {} emails'.format(len(messages)))
        send_emails(messages)
