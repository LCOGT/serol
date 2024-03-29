from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status
from datetime import datetime
from django.db.models import Q

import logging
import json

from status.images import make_request_image
from status.schedule import convert_requestid
from status.models import Progress

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update requests to request id not request group'

    def add_arguments(self, parser):
        parser.add_argument('--request_id', '-rid', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running requests update - {}".format(datetime.now().isoformat())))
        if options['request_id']:
            self.stdout.write("Looking for Progress matching ID={}".format(options['request_id']))
            pgs = Progress.objects.filter(requestid=json.dumps(int(options['request_id'])))
        else:
            pgs = Progress.objects.filter(status='Submitted')
            self.stdout.write("Found {} Progress entries".format(pgs.count()))
        for pg in pgs:
            self.stdout.write("Updating {}".format(pg.requestid))
            newid, msg = convert_requestid(pg.requestid, token=settings.PORTAL_TOKEN)
            if newid:
                pg.requestid = json.dumps(newid)
                pg.save()
                self.stdout.write(self.style.SUCCESS("Update of {} successful".format(newid)))
            else:
                self.stdout.write(self.style.ERROR("Update of {} failed: {}".format(newid, msg)))
        for pg in Progress.objects.filter(~Q(requestid__contains="[")):
            pg.requestid = json.dumps([pg.requestid])
            pg.save()
            self.stdout.write(self.style.SUCCESS("Updated of {} requestid".format(pg.id)))
