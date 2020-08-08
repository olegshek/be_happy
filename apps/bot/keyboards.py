import math

from django.utils import timezone
from telebot import types

from apps.bot import messages
from apps.bot.models import KeyboardButtonsOrdering, Button
from apps.customer.models import Transaction
from apps.store.models import Category, Product
from core import utils


def get_back_button_obj():
    return Button.objects.get(name='back')


def get_checkout_buttons(order_type):
    buttons = []

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='checkout').order_by('ordering'):
        button = keyboard_button.button
        button_name = button.name
        button_text = button.text
        text = button.text
        buttons.append(
            types.InlineKeyboardButton(text, callback_data=f'{button_name};{order_type}')
        )

    return buttons


def language_choice():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = []
    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='language_choice').order_by(
            'ordering'):
        button = keyboard_button.button
        button_name = button.name
        buttons.append(types.InlineKeyboardButton(
            (button.text_ru if button_name == 'ru' else button.text_uz if button_name == 'uz' else button.text_en),
            callback_data=button_name
        ))

    keyboard.add(*buttons)

    return keyboard


def main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = []
    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='main_menu').order_by('ordering'):
        button = keyboard_button.button

        button_name = button.name
        tg_button = types.InlineKeyboardButton(button.text, callback_data=button_name)

        if button_name == 'order':
            keyboard.row(tg_button)
        else:
            buttons.append(tg_button)

    keyboard.add(*buttons)
    return keyboard


def order_type_choice():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    keyboard_buttons_ordering = KeyboardButtonsOrdering.objects.filter(
        keyboard__name='order_type_choice'
    ).order_by('ordering')

    for keyboard_button in keyboard_buttons_ordering:
        button = keyboard_button.button
        buttons.append(types.InlineKeyboardButton(button.text, callback_data=button.name))

    keyboard.add(*buttons)
    return keyboard


def settings():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='settings').order_by('ordering'):
        button = keyboard_button.button
        buttons.append(types.InlineKeyboardButton(button.text, callback_data=button.name))

    keyboard.add(*buttons)
    return keyboard


def product_category(order_type):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button_obj = get_back_button_obj()

    for category in Category.objects.all():
        keyboard.add(types.InlineKeyboardButton(category.name, callback_data=f'{category.id};{order_type}'))

    keyboard.add(*get_checkout_buttons(order_type))
    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=back_button_obj.name))
    return keyboard


def products_list(order_type, category_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    back_button_obj = get_back_button_obj()

    for product in Product.objects.filter(category_id=category_id):
        keyboard.add(types.InlineKeyboardButton(product.name, callback_data=f'{product.id};{order_type}'))

    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=f'{back_button_obj.name};{order_type}'))
    return keyboard


def product_retrieve(order_type, product_id):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    back_button_obj = get_back_button_obj()

    buttons = []
    for i in range(1, 10):
        buttons.append(types.InlineKeyboardButton(i, callback_data=f'{i};{product_id};{order_type}'))

    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(back_button_obj.text,
                                            callback_data=f'{back_button_obj.name};{product_id};{order_type}'))
    return keyboard


def cart(order_type, user_id):
    keyboard = types.InlineKeyboardMarkup()
    checkout_button = Button.objects.get(name='checkout')
    back_button_obj = get_back_button_obj()
    transactions = Transaction.objects.filter(customer_id=user_id, order__isnull=True)

    for transaction in transactions:
        keyboard.add(types.InlineKeyboardButton(f'❌ {transaction.product.name} x {transaction.quantity}',
                                                callback_data=f'{transaction.id};{order_type}'))

    keyboard.add(types.InlineKeyboardButton(f'{messages.total_sum(transactions)}', callback_data='ignore'))

    keyboard.add(types.InlineKeyboardButton(checkout_button.text, callback_data=f'{checkout_button.name};{order_type}'))

    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=f'{back_button_obj.name};{order_type}'))
    return keyboard


def order_time(order_type):
    keyboard = types.InlineKeyboardMarkup()

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='order_time').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.InlineKeyboardButton(button.text, callback_data=f'{button.name};{order_type}'))

    return keyboard


def time_choice(order_type, option=None, time_type=None, time_data=None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    accept_button = Button.objects.get(name='accept')
    back_button_obj = get_back_button_obj()
    order_time = utils.order_time()

    if all([option, time_type, time_data]):
        time_data = timezone.datetime.strptime(time_data, "%H:%M:%S")
        new_timedelta = timezone.timedelta(hours=1) if time_type == 'hour' else timezone.timedelta(minutes=10)
        new_order_time = ((time_data + new_timedelta) if option == 'plus' else (time_data - new_timedelta)).time()

        if new_order_time >= order_time:
            order_time = new_order_time

    time_types = {
        0: 'hour',
        1: 'minute'
    }
    time_data_options = {
        0: order_time.hour,
        1: math.ceil(order_time.minute / 5) * 5
    }

    order_time = timezone.datetime.strptime(f'{time_data_options[0]}:{time_data_options[1]}', '%H:%M').time()
    plus_buttons = []
    minus_buttons = []
    time_buttons = []

    for i in range(2):
        plus_buttons.append(
            types.InlineKeyboardButton('+', callback_data=f'plus;{time_types[i]};{order_time};{order_type}')
        )
        minus_buttons.append(
            types.InlineKeyboardButton('-', callback_data=f'minus;{time_types[i]};{order_time};{order_type}')
        )
        time_buttons.append(types.InlineKeyboardButton(time_data_options[i], callback_data='ignore'))

    keyboard.add(*plus_buttons)
    keyboard.add(*time_buttons)
    keyboard.add(*minus_buttons)

    keyboard.add(
        types.InlineKeyboardButton(accept_button.text, callback_data=f'{accept_button.name};{order_time};{order_type}')
    )
    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=back_button_obj.name))
    return keyboard


def phone_number():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='phone_number').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.KeyboardButton(
            button.text,
            request_contact=True if button.name == 'phone_number' else None
        ))

    return keyboard


def location():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='location').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.KeyboardButton(
            button.text,
            request_location=True if button.name == 'location' else None
        ))

    return keyboard


def payment_types():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='payment_types').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.KeyboardButton(button.text))

    return keyboard


def confirm_order():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='confirm_order').order_by('ordering'):
        keyboard.add(types.KeyboardButton(keyboard_button.button.text))

    return keyboard


def pay():
    keyboard = types.InlineKeyboardMarkup()
    back_button_obj = get_back_button_obj()

    for keyboard_button in KeyboardButtonsOrdering.objects.filter(keyboard__name='pay').order_by('ordering'):
        button = keyboard_button.button
        keyboard.add(types.InlineKeyboardButton(button.text, pay=True if button.name == 'pay' else None))

    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=back_button_obj.name))
    return keyboard


def back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = get_back_button_obj()
    keyboard.add(types.KeyboardButton(button.text))
    return keyboard


def inline_back_keyboard():
    back_button_obj = get_back_button_obj()
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(back_button_obj.text, callback_data=back_button_obj.name))
    return keyboard


remove_keyboard = types.ReplyKeyboardRemove()
