from django.conf import settings
from django.utils import translation

from apps.bot import messages
from apps.customer.models import Order
from config.celery import app


@app.task
def send_order_to_channel(order_id):
    from apps.bot.telegram_views import bot

    translation.activate('ru')
    order = Order.objects.get(id=order_id)
    location = order.location
    channel_id = settings.CHANNEL_ID

    message = messages.order_retrieve(order).replace('Ваш заказ:', '')
    location_message = None

    if location:
        if location.latitude and location.longitude:
            location_message = bot.send_location(channel_id, location.latitude, location.longitude)

    bot.send_message(channel_id, message, reply_to_message_id=location_message.message_id if location_message else None)
