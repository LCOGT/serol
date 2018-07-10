from django.core.management.base import BaseCommand, CommandError

from status.images import make_request_image

class Command(BaseCommand):
    help = 'Update status of submitted observations'

    def add_arguments(self, parser):
        parser.add_argument('--requestid')
        parser.add_argument('--name')

    def handle(self, *args, **options):
        make_request_image(options['requestid'], options['name'])
