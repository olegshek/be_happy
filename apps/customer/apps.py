from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'apps.customer'

    def ready(self):
        from apps.customer import telegram_views

