import functools

from apps.bot.models import Keyboard


def keyboard_callback_query(keyboard_name, query):
    buttons = Keyboard.objects.get(name=keyboard_name).buttons.exclude(name='back').values_list('name', flat=True)

    return query.data.split(';')[0] in map(str, buttons)


def step_handler(func):
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.text == '/start':
            from apps.customer.telegram_views import start_processing
            return start_processing(message)
        return func(message, *args, **kwargs)

    return wrapper

