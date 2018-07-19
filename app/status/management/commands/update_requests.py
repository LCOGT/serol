from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from rest_framework import status

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
        if options['request_id']:
            logger.info("Looking for Progress matching ID={}".format(options['request_id']))
            pgs = Progress.objects.filter(requestid=options['request_id'])
        else:
            pgs = Progress.objects.filter(state=Submitted)
            logger.info("Found {} Progress entries".format(pgs.count()))
        for pg in pgs:
            logger.info("Updating {}".format(pg.requestid))
            resp = update_status(pg.requestid, token=settings.PORTAL_TOKEN)
            logger.info(resp.status_code)
            if status.is_success(resp.status_code):
                logger.info("Update of {} successful".format(pg.requestid))
                make_request_image(request_id=pg.requestid, category=pg.challenge.avm_code, targetname=pg.target)
            else:
                logger.info("Update of {} failed - {}".format(pg.requestid, resp.data))
