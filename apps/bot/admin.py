from django.contrib import admin
from django.contrib.auth.models import User, Group
from modeltranslation.admin import TranslationAdmin

from apps.bot.models import Button, Message


admin.site.unregister(User)
admin.site.unregister(Group)


class ButtonAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('text_ru', 'text_uz')
    fields = ('text_ru', 'text_uz')
    search_fields = ('text_ru', 'text_uz')


class MessageAdmin(TranslationAdmin):
    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    list_display = ('text_ru', 'text_uz')
    fields = ('text_ru', 'text_uz')
    search_fields = ('text_ru', 'text_uz')


admin.site.register(Button, ButtonAdmin)
admin.site.register(Message, MessageAdmin)
