from uuid import uuid4

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=30, verbose_name=_('Name'))

    class Meta:
        verbose_name = _('Product category')
        verbose_name_plural = _('Product categories')

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',
                                 verbose_name=_('Product Category'))
    name = models.CharField(max_length=30, verbose_name=_('Name'))
    image = models.ImageField(null=True, blank=True, verbose_name=_('Image'))
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Description'))
    price = models.IntegerField(default=0, verbose_name=_('Price'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name
