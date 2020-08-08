import functools

from django.utils import translation, timezone

from apps.bot.models import Message
from apps.customer.models import Customer


def set_language(func):
    @functools.wraps(func)
    def wrapper(data, *args, **kwargs):
        subscriber = Customer.objects.filter(id=data.from_user.id).first()
        translation.activate('ru' if not subscriber else subscriber.language)
        return func(data, *args, **kwargs)

    return wrapper


def get_message(title):
    return Message.objects.get(title=title).text


def order_time():
    return (timezone.now().astimezone() + timezone.timedelta(minutes=60)).time()
