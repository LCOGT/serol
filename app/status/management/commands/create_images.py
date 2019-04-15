from datetime import datetime
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import get_valid_filename
from tempfile import NamedTemporaryFile

import os
import logging

from status.images import make_request_image
from status.views import update_status
from status.models import Progress

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update requests and call pipeline'

    def add_arguments(self, parser):
        parser.add_argument('--request_id', '-rid', help="[Optional] Request ID to update")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running image pipeline - {}".format(datetime.now().isoformat())))
        if options['request_id']:
            pgs = Progress.objects.filter(requestid=options['request_id'])
            self.stdout.write("Looking for Progress matching ID={}".format(options['request_id']))
        else:
            # Pick up any successful observation with no image
            pgs = Progress.objects.filter(status__in=('Observed','Identify','Analyse','Investigate','Summary'), image_status=0)
            self.stdout.write("Processing {} observations".format(len(pgs)))
        for pg in pgs:
            self.stdout.write("Download and make JPEG  - ReqID {}  ProgID {}".format(pg.requestid, pg.id))
            with NamedTemporaryFile() as tmpfile:
                image_status = make_request_image(filename=tmpfile.name, request_id=pg.requestid, category=pg.challenge.avm_code, targetname=pg.target)
                self.stdout.write("Processed {}: image of {}, status {}".format(pg.requestid, pg.target, image_status))
                if image_status > 0:
                    name = "{}-{}.jpg".format(pg.target.replace(" ",""), pg.requestid)
                    name = get_valid_filename(name)
                    # with open(tmpfile, 'rb') as f:
                    pg.image_file.save(name, File(tmpfile), save=True)
                    pg.image_status = image_status
                    pg.last_update = datetime.now()
                    if pg.status == 'Observed':
                        pg.identify()
                    pg.save()
                    self.stdout.write(self.style.SUCCESS("Successfully created image for {}".format(pg.id)))
