from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status
from datetime import datetime

import logging
import json

from status.images import make_request_image
from status.views import update_status
from status.models import Progress

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update requests and call pipeline'

    def add_arguments(self, parser):
        parser.add_argument('--requestgroup', '-rid', help="[Optional] Request Group to update")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running requests update - {}".format(datetime.now().isoformat())))
        if options['requestgroup']:
            self.stdout.write("Looking for Progress matching ID={}".format(options['requestgroup']))
            pgs = Progress.objects.filter(requestgroup=options['requestgroup'])
        else:
            pgs = Progress.objects.filter(status='Submitted')
            self.stdout.write("Found {} Progress entries".format(pgs.count()))
        for pg in pgs:
            self.stdout.write("Updating {}".format(pg.requestid))
            for rid in json.loads(pg.requestid):
                resp = update_status(progressid=pg.id, requestid=rid, token=settings.PORTAL_TOKEN, archive_token=settings.ARCHIVE_TOKEN)
                if status.is_success(resp.status_code):
                    self.stdout.write(self.style.SUCCESS("Update of {} successful".format(pg.requestid)))
                    break
                else:
                    self.stdout.write(self.style.ERROR("Update of {} failed - {}".format(pg.requestid, resp.data)))
