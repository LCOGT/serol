from datetime import datetime
from tempfile import NamedTemporaryFile
import json

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import get_valid_filename

from status.images import make_request_image
from status.views import update_status
from status.models import Progress

from notify.views import send_notifications


class Command(BaseCommand):
    help = 'Update requests and call pipeline'

    def add_arguments(self, parser):
        parser.add_argument('--requestgroup', '-rid', help="[Optional] Request group to update")

    def handle(self, *args, **options):
        success = []
        self.stdout.write(self.style.WARNING("Running image pipeline - {}".format(datetime.now().isoformat())))
        if options['requestgroup']:
            pgs = Progress.objects.filter(requestgroup=options['requestgroup'])
            self.stdout.write("Looking for Progress matching ID={}".format(options['requestgroup']))
        else:
            # Pick up any successful observation with no image
            pgs = Progress.objects.filter(status__in=('Observed','Identify','Analyse','Investigate','Summary'), image_status=0)
            self.stdout.write("Processing {} observations".format(len(pgs)))
        for pg in pgs:
            try:
                rid = str(json.loads(pg.requestid)[0])
            except:
                self.stderr.write(f"Progress id {pg.id} has no requests")
                continue
            self.stdout.write("Download and make JPEG  - ReqID {}  ProgID {}".format(rid, pg.id))
            with NamedTemporaryFile() as tmpfile:
                image_status = make_request_image(filename=tmpfile.name, request_id=rid, category=pg.challenge.avm_code, targetname=pg.target, frameid=pg.frameids)
                self.stdout.write("Processed {}: image of {}, status {}".format(rid, pg.target, image_status))
                if image_status > 0:
                    name = "{}-{}.jpg".format(pg.target.replace(" ",""), rid)
                    name = get_valid_filename(name)
                    pg.image_file.save(name, File(tmpfile), save=True)
                    pg.image_status = image_status
                    pg.last_update = datetime.now()
                    if pg.status == 'Observed':
                        pg.identify()
                    pg.save()
                    success.append(pg)
                    self.stdout.write(self.style.SUCCESS("Successfully created image for {}".format(pg.id)))
            # Email all successfully completed progresses
            send_notifications(success)
