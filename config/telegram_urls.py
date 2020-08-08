from django.conf import settings
from django.urls import path

from apps.bot.telegram_views import webhook

urlpatterns = [
    path(f'telegram/{settings.TELEGRAM_TOKEN}/', webhook)
]