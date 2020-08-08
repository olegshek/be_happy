from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = 'apps.store'

    def ready(self):
        from apps.store import telegram_views
