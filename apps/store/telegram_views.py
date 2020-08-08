from django.conf import settings
from django.utils import timezone
from telebot.apihelper import ApiException

from apps.bot import bot, validators, keyboards, messages, activity
from apps.bot.models import Button
from apps.customer.models import Transaction, Order, Customer, Location, ReviewMessage, CustomerActivityEvent
from apps.store.models import Category, Product
from apps.store.tasks import send_order_to_channel
from apps.store.utils import create_order_transaction
from core import utils


def send_product_detail(product, order_type, user_id, message_id):
    product_message = messages.product_retrieve(product)
    product_keyboard = keyboards.product_retrieve(order_type, product.id)
    try:
        bot.delete_message(user_id, message_id)
    except ApiException:
        pass

    if product.image:
        bot.send_chat_action(user_id, 'upload_photo')
        bot.send_photo(user_id, product.image, product_message, reply_markup=product_keyboard, parse_mode='HTML')
    else:
        bot.send_message(user_id, product_message, reply_markup=product_keyboard, parse_mode='HTML')


@bot.callback_query_handler(lambda query: validators.keyboard_callback_query('main_menu', query))
@utils.set_language
def main_menu_processing(query):
    user_id = query.from_user.id
    data = query.data
    message_id = query.message.message_id

    if data == 'order':
        Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).delete()
        Transaction.objects.filter(customer_id=user_id, order__isnull=True).delete()
        bot.edit_message_text(utils.get_message('category_choice'), user_id, query.message.message_id,
                              reply_markup=keyboards.product_category('DELIVERY'))

    if data == 'information':
        try:
            bot.delete_message(user_id, message_id)
        except ApiException:
            pass

        bot.send_location(user_id, settings.ORIGIN_LATITUDE, settings.ORIGIN_LONGITUDE)
        bot.send_message(user_id, utils.get_message('information'), reply_markup=keyboards.inline_back_keyboard())

    if data == 'settings':
        bot.edit_message_text(utils.get_message('settings'), user_id, message_id, reply_markup=keyboards.settings())

    if data == 'review':
        try:
            bot.delete_message(user_id, message_id)
        except ApiException:
            pass

        bot.send_message(user_id, utils.get_message('review_required'), reply_markup=keyboards.back_keyboard())
        bot.register_next_step_handler(query.message, review_processing)

    CustomerActivityEvent.objects.filter(customer_id=user_id).delete()


@validators.step_handler
@utils.set_language
def review_processing(message):
    user_id = message.from_user.id
    text = message.text
    back_button = Button.objects.get(name='back')

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)
        return bot.send_message(user_id, utils.get_message('main_menu'), reply_markup=keyboards.main_menu())

    ReviewMessage.objects.create(customer_id=user_id, message=text)
    bot.send_message(user_id, utils.get_message('review_save'), reply_markup=keyboards.remove_keyboard)
    bot.send_message(user_id, utils.get_message('main_menu'), reply_markup=keyboards.main_menu())


@bot.callback_query_handler(lambda query: validators.keyboard_callback_query('checkout', query))
@utils.set_language
def checkout_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id
    button_name, order_type = query.data.split(';')
    transactions = Transaction.objects.filter(customer_id=user_id, order__isnull=True)

    if not transactions:
        try:
            return bot.edit_message_text(utils.get_message('empty_cart'), user_id, message_id,
                                         reply_markup=keyboards.product_category(order_type))
        except ApiException:
            return

    message = utils.get_message('order_type_choice')
    keyboard = keyboards.order_type_choice()
    if button_name == 'cart':
        message = utils.get_message('cart')
        keyboard = keyboards.cart(order_type, user_id)

    bot.edit_message_text(message, user_id, message_id, reply_markup=keyboard)
    return activity.register(user_id, 'product_category', order_type)


@bot.callback_query_handler(
    lambda query: query.data.split(';')[0] in map(str, Category.objects.values_list('id', flat=True))
)
@utils.set_language
def product_category_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id

    category_id, order_type = query.data.split(';')
    text = utils.get_message('products_list')
    keyboard = keyboards.products_list(order_type, category_id)

    bot.edit_message_text(
        text,
        user_id,
        message_id,
        reply_markup=keyboard
    )
    return activity.register(user_id, 'product_category', order_type)


@bot.callback_query_handler(
    lambda query: query.data.split(';')[0] in map(str, Product.objects.values_list('id', flat=True))
)
@utils.set_language
def products_list_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id

    product_id, order_type = query.data.split(';')

    product = Product.objects.filter(id=product_id).first()

    if not product:
        return bot.edit_message_text(utils.get_message('temporary_unavailable'), user_id, message_id,
                                     reply_markup=keyboards.product_category(order_type))

    send_product_detail(product, order_type, user_id, message_id)
    return activity.register(user_id, 'products_list', f'{order_type};{product.category_id}')


@bot.callback_query_handler(lambda query: query.data.split(';')[0].isdigit())
@utils.set_language
def product_quantity_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id
    quantity, product_id, order_type = query.data.split(';')

    transaction_created, data = create_order_transaction(user_id, product_id, quantity)
    data_is_digit = data.isdigit()
    message = utils.get_message(data)

    try:
        bot.delete_message(user_id, message_id)
    except ApiException:
        pass

    bot.send_message(user_id, message,
                     reply_markup=keyboards.product_category(order_type) if not data_is_digit else None)

    if data_is_digit:
        product = Product.objects.get(id=product_id)
        send_product_detail(product, order_type, user_id, message_id)


@bot.callback_query_handler(
    lambda query: query.data.split(';')[0] in map(str, Transaction.objects.values_list('id', flat=True))
)
@utils.set_language
def cart_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id
    transaction_id, order_type = query.data.split(';')

    Transaction.objects.get(id=transaction_id).delete()

    if not Transaction.objects.filter(customer_id=user_id, order__isnull=True):
        return bot.edit_message_text(utils.get_message('empty_cart'), user_id, message_id,
                                     reply_markup=keyboards.product_category(order_type))

    return bot.edit_message_text(utils.get_message('cart'), user_id, message_id,
                                 reply_markup=keyboards.cart(order_type, user_id))


@bot.callback_query_handler(lambda query: validators.keyboard_callback_query('order_type_choice', query))
@utils.set_language
def order_type_choice_processing(query):
    user_id = query.from_user.id
    message_id = query.message.message_id
    customer = Customer.objects.get(id=user_id)
    order = Order.objects.create(customer_id=user_id, order_type=query.data)
    order.transactions.set(Transaction.objects.filter(customer_id=user_id, order__isnull=True))

    try:
        bot.delete_message(user_id, message_id)
    except ApiException:
        pass

    if not customer.full_name:
        bot.send_message(user_id, utils.get_message('full_name_required'), reply_markup=keyboards.back_keyboard())
        return bot.register_next_step_handler(query.message, save_full_name)

    bot.send_message(user_id, utils.get_message('phone_number_required'), reply_markup=keyboards.phone_number())
    bot.register_next_step_handler(query.message, save_phone_number, False)


@validators.step_handler
@utils.set_language
def save_full_name(message):
    user_id = message.from_user.id
    text = message.text

    customer = Customer.objects.get(id=user_id)
    back_button = Button.objects.get(name='back')

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)

        unconfirmed_order = Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).first()
        order_type = unconfirmed_order.order_type
        bot.send_message(
            user_id,
            utils.get_message('time_choice'),
            reply_markup=keyboards.order_time(order_type)
        )
        unconfirmed_order.delete()
        return unconfirmed_order.delete()

    customer.full_name = text
    customer.save()
    bot.send_message(user_id, utils.get_message('phone_number_required'), reply_markup=keyboards.phone_number())
    return bot.register_next_step_handler(message, save_phone_number, True)


@validators.step_handler
@utils.set_language
def save_phone_number(message, from_save_full_name):
    user_id = message.from_user.id
    text = message.text
    contact = message.contact

    customer = Customer.objects.get(id=user_id)
    back_button = Button.objects.get(name='back')

    unconfirmed_order = Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).first()
    order_type = unconfirmed_order.order_type

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)

        if from_save_full_name:
            bot.send_message(user_id, utils.get_message('full_name_required'), reply_markup=keyboards.back_keyboard())
            return bot.register_next_step_handler(message, save_full_name)
        bot.send_message(
            user_id,
            utils.get_message('order_type_choice'),
            reply_markup=keyboards.order_type_choice()
        )
        return unconfirmed_order.delete()

    customer.phone_number = contact.phone_number if contact else text
    customer.save()

    if order_type == 'DELIVERY':
        bot.send_message(user_id, utils.get_message('location_required'), reply_markup=keyboards.location())
        return bot.register_next_step_handler(message, save_location, from_save_full_name)

    bot.send_message(user_id, '✔️', reply_markup=keyboards.remove_keyboard)
    bot.send_message(user_id, messages.order_retrieve(unconfirmed_order), reply_markup=keyboards.confirm_order(),
                     parse_mode='HTML')
    bot.register_next_step_handler(message, confirm_order, from_save_full_name)


@validators.step_handler
@utils.set_language
def save_location(message, from_save_full_name):
    user_id = message.from_user.id
    text = message.text
    back_button = Button.objects.get(name='back')
    location_message = message.location

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)

        bot.send_message(user_id, utils.get_message('phone_number_required'), reply_markup=keyboards.phone_number())
        return bot.register_next_step_handler(message, save_phone_number, from_save_full_name)

    location_data = dict(
        latitude=location_message.latitude if location_message else None,
        longitude=location_message.longitude if location_message else None,
        address=text if text else None
    )

    location = Location.objects.create(**location_data)
    order = Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).first()
    order.location = location
    order.save()

    bot.send_message(user_id, '✔️', reply_markup=keyboards.remove_keyboard)
    bot.send_message(user_id, messages.order_retrieve(order), reply_markup=keyboards.confirm_order(),
                     parse_mode='HTML')
    bot.register_next_step_handler(message, confirm_order, from_save_full_name)


@validators.step_handler
@utils.set_language
def confirm_order(message, from_save_full_name):
    user_id = message.from_user.id
    text = message.text
    back_button = Button.objects.get(name='back')
    order = Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).first()

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)

        if order.order_type == 'PICKUP':
            bot.send_message(user_id, utils.get_message('phone_number_required'), reply_markup=keyboards.phone_number())
            return bot.register_next_step_handler(message, save_phone_number, from_save_full_name)

        bot.send_message(user_id, utils.get_message('location_required'), reply_markup=keyboards.location())
        return bot.register_next_step_handler(message, save_location, from_save_full_name)

    confirm_button = Button.objects.filter(text=text).first()

    if not confirm_button or confirm_button.name != 'confirm_order':
        return bot.register_next_step_handler(message, confirm_order, from_save_full_name)

    order = Order.objects.filter(customer_id=user_id, confirmed_at__isnull=True).first()

    order.confirmed_at = timezone.now()
    order.save()
    send_order_to_channel.delay(order.id)
    activity.delete_activity_event(user_id)
    bot.send_message(user_id, utils.get_message('success_order') % {'order_id': order.order_id},
                     reply_markup=keyboards.remove_keyboard)
    return bot.send_message(user_id, utils.get_message('main_menu'), reply_markup=keyboards.main_menu())
