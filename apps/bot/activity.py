from telebot.apihelper import ApiException

from apps.bot import keyboards
from apps.customer.models import CustomerActivityEvent, Customer
from core import utils


def register(customer_id, event, data=None):
    CustomerActivityEvent.objects.create(customer_id=customer_id, event=event, data=data)


def delete_activity_event(customer_id):
    CustomerActivityEvent.objects.filter(customer_id=customer_id).delete()


def back(customer_id, message_id):
    from apps.bot.telegram_views import bot

    activity_event = CustomerActivityEvent.objects.filter(customer_id=customer_id).order_by('-created_at').first()
    event = activity_event.event if activity_event else None
    data = activity_event.data if activity_event else None

    message = ''
    keyboard = keyboards.main_menu()

    if event == 'order_type_choice':
        message = utils.get_message('order_type_choice')
        keyboard = keyboards.order_type_choice()

    if event == 'product_category':
        message = utils.get_message('category_choice')
        keyboard = keyboards.product_category(data)

    if event == 'products_list':
        message = utils.get_message('products_list')
        keyboard = keyboards.products_list(*data.split(';'))

    if event == 'time_choice':
        message = utils.get_message('time_choice')
        keyboard = keyboards.time_choice(data)

    if event == 'payment':
        message = utils.get_message('payment_type')
        keyboard = keyboards.payment_types()

    try:
        bot.delete_message(customer_id, message_id)
    except ApiException:
        pass

    if not message:
        message = utils.get_message('main_menu')
        delete_activity_event(customer_id)

    tg_message = bot.send_message(customer_id, message, reply_markup=keyboard)

    if event == 'payment':
        from apps.store.telegram_views import save_payment_type
        bot.register_next_step_handler(tg_message, save_payment_type, eval(data))

    if activity_event:
        activity_event.delete()
