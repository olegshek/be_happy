from django.utils import translation
from telebot.apihelper import ApiException

from apps.bot import bot, keyboards, validators, activity
from apps.bot.models import Button
from apps.customer.models import Customer
from core import utils
from core.utils import get_message, set_language


@bot.message_handler(commands=['start'])
@set_language
def start_processing(message):
    user_id = message.from_user.id
    customer, _ = Customer.objects.update_or_create(
        id=user_id,
        defaults=dict(
            username=message.chat.username
        )
    )

    activity.delete_activity_event(user_id)
    bot.send_message(user_id, get_message('greeting'), reply_markup=keyboards.remove_keyboard)
    bot.send_message(user_id, get_message('language_choice'), reply_markup=keyboards.language_choice())


@bot.callback_query_handler(lambda query: validators.keyboard_callback_query('language_choice', query))
def language_choice_processing(query):
    user_id = query.from_user.id
    language = query.data
    Customer.objects.filter(id=user_id).update(language=language)
    translation.activate(language)
    activity.delete_activity_event(user_id)
    bot.edit_message_text(get_message('main_menu'), user_id, query.message.message_id,
                          reply_markup=keyboards.main_menu())


@bot.callback_query_handler(lambda query: validators.keyboard_callback_query('settings', query))
@utils.set_language
def settings_processing(query):
    user_id = query.from_user.id
    message = query.message
    message_id = message.message_id
    data = query.data

    if data == 'full_name_change':
        try:
            bot.delete_message(user_id, message_id)
        except ApiException:
            pass

        bot.send_message(user_id, utils.get_message('full_name_required'), reply_markup=keyboards.back_keyboard())
        return bot.register_next_step_handler(message, full_name_change)

    if data == 'language_change':
        bot.edit_message_text(get_message('language_choice'), user_id, message_id,
                              reply_markup=keyboards.language_choice())


@validators.step_handler
@utils.set_language
def full_name_change(message):
    user_id = message.from_user.id
    text = message.text
    back_button = Button.objects.get(name='back')

    if text == back_button.text:
        bot.send_message(user_id, '🔙', reply_markup=keyboards.remove_keyboard)
        return bot.send_message(user_id, utils.get_message('settings'), reply_markup=keyboards.settings())

    Customer.objects.filter(id=user_id).update(full_name=text)
    activity.delete_activity_event(user_id)
    bot.send_message(user_id, '✔️', reply_markup=keyboards.remove_keyboard)
    bot.send_message(user_id, utils.get_message('main_menu'), reply_markup=keyboards.main_menu())

