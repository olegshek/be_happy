import telebot
from django.conf import settings
from telebot import apihelper

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)