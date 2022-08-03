from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
import json

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import get_valid_filename
from django.urls import reverse
from user_messages import api

from status.request_formats import best_observing_time

class Command(BaseCommand):
    help = 'Update requests to request id not request group'

    def add_arguments(self, parser):
        parser.add_argument('--date', '-d', help="[Optional] Start date")

    def handle(self, *args, **options):
        siteset = ['coj','tfn']
        now = datetime.utcnow()
        for day in range(0,28):
            date = now + timedelta(days=day)
            dates = []
            for site in siteset:
                dates.extend(best_observing_time(site))
            self.stdout.write(f"{date.isoformat()} - Num dates {len(dates)}")
