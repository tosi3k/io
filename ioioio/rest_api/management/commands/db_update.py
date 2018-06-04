from django.core.management.base import BaseCommand, CommandError
import os
import json
from rest_api.maps import patch_all, update_paths
from ioioio import settings

KEYS_FILENAME = 'api_keys.json'

class Command(BaseCommand):
    help = 'Updates paths, adds new paths for stations if necesssary'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        keys_directory = os.path.join('data', KEYS_FILENAME)
        keys_filename = os.path.join(settings.BASE_DIR, keys_directory)
        print(keys_filename)
        if not os.path.isfile(keys_filename):
            raise CommandError('File %s does not exist' % keys_filename)
        else:
            with open(keys_filename, 'r') as keys_f:
                keys = json.load(keys_f)["keys"]

            # patch_all(keys[0])
            for key in keys:
                update_paths(key)

            self.stdout.write(self.style.SUCCESS('Successfully updated database'))
