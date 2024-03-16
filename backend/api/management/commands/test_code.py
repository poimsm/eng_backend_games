# Framework
from django.core.management.base import BaseCommand
from django.conf import settings
import traceback

# Custom


class Command(BaseCommand):
    help = 'Testing whatever code'

    def handle(self, *args, **kwargs): 
        print(settings.SITE_DOMAIN)
