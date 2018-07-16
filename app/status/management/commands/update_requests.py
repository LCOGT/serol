from django.core.management.base import BaseCommand, CommandError

from status.views import update_status
from status.models import Progress

class Command(BaseCommand):
    help = 'Update requests and call pipeline'

    def add_arguments(self, parser):
        parser.add_argument('--request_id', '-rid', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        if options['request_id']:
            update_status(options['request_id'], token=settings.PORTAL_TOKEN)
        else:
            for pg in Progress.objects.filter(state=Submitted):
                update_status(pg.requestid, token=settings.PORTAL_TOKEN)
