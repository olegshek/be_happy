import requests
from django.apps import AppConfig
from django.conf import settings


class BotConfig(AppConfig):
    name = 'apps.bot'

    def ready(self):
        url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook'
        querystring = dict(
            url=f'{settings.BACKEND_ADDRESS}/telegram/{settings.TELEGRAM_TOKEN}/'
        )
        response = requests.request("GET", url, params=querystring)
        print(response.content.decode('utf-8'))
