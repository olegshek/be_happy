import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

settings.ROOT_URLCONF = 'config.telegram_urls'

application = get_wsgi_application()