from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status
from datetime import datetime
from django.db.models import Q

import logging
import json

from status.schedule import  get_headers_frameid
from status.models import Progress

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update observation location from frameid'

    def add_arguments(self, parser):
        parser.add_argument('--requestgroup', '-r', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running requests update - {}".format(datetime.now().isoformat())))
        if options['requestgroup']:
            self.stdout.write("Looking for Progress matching ID={}".format(options['requestgroup']))
            pgs = Progress.objects.filter(requestgroup=options['requestgroup'])
        else:
            pgs = Progress.objects.filter(status__in=['Identify','Observed','Summary','Analyse'], siteid__isnull=True)
            self.stdout.write("Found {} Progress entries".format(pgs.count()))
        for pg in pgs:
            self.stdout.write("Updating {} ({})".format(pg.id, pg.pk))
            frameid = pg.frameids
            data = get_headers_frameid(frameid=frameid, token=settings.PORTAL_TOKEN)
            if data:
                pg.siteid = data['siteid']
                pg.save()
                self.stdout.write(self.style.SUCCESS("Update of {} successful".format(pg)))
            else:
                self.stdout.write(self.style.ERROR("Update of {} failed".format(pg.id)))
