import json

import telebot
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.bot import bot
from apps.bot.activity import back
from core import utils


@csrf_exempt
def webhook(request):
    if request.method != 'POST':
        raise Http404

    json_data = json.loads(request.body, encoding='utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return HttpResponse('')


@bot.callback_query_handler(lambda query: 'back' in query.data)
@utils.set_language
def back_processing(query):
    back(query.from_user.id, query.message.message_id)


@bot.channel_post_handler(content_types=['text'])
def test(message):
    pass

