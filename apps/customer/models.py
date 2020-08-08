from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import UUIDField, F, Sum, Max
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.store.models import Product


def _generate_order_id():
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_id = Order.objects.filter(confirmed_at__gte=today).aggregate(max_id=Coalesce(Max('order_id'), 0))['max_id']
    return last_id + 1


class Customer(models.Model):
    id = models.IntegerField(primary_key=True, editable=False, unique=True)
    username = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Full name'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone number'))
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='ru', verbose_name=_('Language'))

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.phone_number


class Location(models.Model):
    latitude = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Latitude'))
    longitude = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Longitude'))
    address = models.TextField(null=True, verbose_name=_('Address'))
    distance = models.FloatField(default=0.0, verbose_name=_('Distance'))

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

    def __str__(self):
        address = self.address
        return address if address else str(self.id)


class Order(models.Model):
    STATUSES = (
        ('ACCEPTED', _('ACCEPTED')),
        ('EN ROUTE', _('EN ROUTE')),
        ('DELIVERED', _('DELIVERED')),
        ('PENDING', _('PENDING')),
        ('COOKING', _('COOKING')),
        ('CANCELLED', _('CANCELLED'))
    )

    ORDER_TYPES = (
        ('DELIVERY', _('🚘 Delivery')),
        ('PICKUP', _('🏃 Pickup'))
    )

    PAYMENT_TYPES = (
        ('CASH', _('💵 Cash')),
        ('PAYME', '💳 Payme')
    )

    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    order_id = models.IntegerField(default=_generate_order_id, verbose_name=_('Order id'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Customer'))
    location = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True, related_name='orders',
                                    verbose_name=_('Location'))
    order_type = models.CharField(max_length=8, choices=ORDER_TYPES, default='DELIVERY', verbose_name=_('Order type'))

    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Confirmed at'))
    status = models.CharField(max_length=40, choices=STATUSES, default='PENDING', verbose_name=_('Status'))

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ('-confirmed_at', '-order_id')
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    @property
    def total_sum(self):
        transactions = self.transactions.annotate(sum=F('quantity')*F('product__price'))
        return transactions.aggregate(tran_sum=Coalesce(Sum('sum'), 0))['tran_sum']

    def __str__(self):
        return str(self.id)


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='transactions',
                                 verbose_name=_('Customer'))
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='transactions',
                              verbose_name=_('Order'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions',
                                verbose_name=_('Product'))
    quantity = models.IntegerField(default=0, verbose_name=_('Quantity'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Created at'))

    @property
    def total_sum(self):
        return self.quantity * self.product.price

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'


class CustomerActivityEvent(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='history_events')
    event = models.CharField(max_length=200)
    data = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)


class ReviewMessage(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    message = models.TextField(verbose_name=_('Message'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='review_messages',
                                 verbose_name=_('Customer'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Review message')
        verbose_name_plural = _('Review messages')

    def __str__(self):
        return str(self.id)
