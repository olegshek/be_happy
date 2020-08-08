from modeltranslation import translator

from apps.store.models import Category, Product
from core.translation import TranslationOptionsMixin


@translator.register(Category)
class CategoryOptions(TranslationOptionsMixin):
    fields = ('name', )


@translator.register(Product)
class ProductOptions(TranslationOptionsMixin):
    fields = ('name', 'description')
