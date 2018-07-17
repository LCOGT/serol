from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status

from status.images import make_request_image
from status.views import update_status
from status.models import Progress

class Command(BaseCommand):
    help = 'Update requests and call pipeline'

    def add_arguments(self, parser):
        parser.add_argument('--request_id', '-rid', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        if options['request_id']:
            pgs = Progress.objects.filter(requestid=options['request_id'])
        else:
            pgs = Progress.objects.filter(state=Submitted)
        for pg in pgs:
            resp = update_status(pg.requestid, token=settings.PORTAL_TOKEN)
            if status.is_success(resp.status_code):
                make_request_image(request_id=pg.requestid, category=pg.challenge.avm_code, targetname=pg.target)
