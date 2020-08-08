from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _

from apps.bot.models import Message


def product_retrieve(product):
    description = product.description if product.description else ''
    return Message.objects.get(title='product_retrieve').text % {
        'name': product.name,
        'description': description,
        'price': str(product.price)
    }


def order_retrieve(order):
    full_name = order.customer.full_name
    res = Message.objects.get(title='order_retrieve').text % {
        'order_id': order.order_id,
        'full_name': full_name if full_name else '',
        'phone_number': order.customer.phone_number,
        'order_type': order.get_order_type_display()
    }
    if order.order_type == 'DELIVERY' and order.location:
        res += f"\n{str(_('Address'))}: {order.location.address}"

    return res + invoice_retrieve(order)


def total_sum(transactions):
    total = transactions.annotate(sum=F('quantity')*F('product__price')).aggregate(total_sum=Sum('sum'))['total_sum']
    return Message.objects.get(title='total_sum').text % {'total_sum': str(total)}


def invoice_retrieve(order):
    currency = str(_('sum'))
    transactions = order.transactions.all()

    res = ''
    for transaction in transactions:
        res += f'\n\n{transaction.product.name}\n' \
               f'{transaction.quantity} x {transaction.product.price} = {transaction.total_sum} {currency}'

    res += f"\n\n{Message.objects.get(title='total_sum').text % {'total_sum': str(order.total_sum)}}"
    return res
