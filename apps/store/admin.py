from django import forms
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from apps.store.models import Product, Category


class CategoryAdmin(TranslationAdmin):
    list_display = ('name_ru', 'name_uz')
    fields = ('name_ru', 'name_uz')
    readonly_fields = ('id', )
    search_fields = ('name_uz', 'name_ru')


class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)

        for field_name in filter(lambda key: 'description' in key, self.fields.keys()):
            self.fields[field_name].required = False


class ProductAdmin(TranslationAdmin):
    form = ProductAdminForm
    fields = ('category', 'name_ru', 'name_uz', 'image', 'description', 'price')
    search_fields = ('name_uz', 'name_ru')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
