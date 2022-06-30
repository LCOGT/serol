from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status
from datetime import datetime
from django.db.models import Q

import logging
import json

from status.schedule import  get_observation_frameid
from status.models import Progress

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update requests to request id not request group'

    def add_arguments(self, parser):
        parser.add_argument('--requestgroup', '-r', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running requests update - {}".format(datetime.now().isoformat())))
        if options['requestgroup']:
            self.stdout.write("Looking for Progress matching ID={}".format(options['requestgroup']))
            pgs = Progress.objects.filter(requestgroup=options['requestgroup'])
        else:
            pgs = Progress.objects.filter(status__in=['Identify','Observed','Summary','Analyse'], ra__isnull=True)
            self.stdout.write("Found {} Progress entries".format(pgs.count()))
        for pg in pgs:
            self.stdout.write("Updating {}".format(pg.requestgroup))
            requestid = json.loads(pg.requestid)[0]
            data = get_observation_frameid(requestid=requestid, token=settings.PORTAL_TOKEN)
            if data:
                pg.frameids = data['frameid']
                pg.ra = data['ra']
                pg.dec = data['dec']
                pg.obsdate = data['date'][0:19]
                pg.save()
                self.stdout.write(self.style.SUCCESS("Update of {} successful".format(pg)))
            else:
                self.stdout.write(self.style.ERROR("Update of {} failed".format(pg.id)))
