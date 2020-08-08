from django.db import transaction
from apps.customer.models import Transaction
from apps.store.models import Product


def product_text(product):
    description = product.description if product.description else ''
    return f'<b>{product.name}</b>\n\n' \
           f'<i>{description}</i>\n\n'


def create_order_transaction(user_id, product_id, quantity):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return False, 'temporary_unavailable'

    with transaction.atomic():
        order_transaction, _ = Transaction.objects.get_or_create(customer_id=user_id, product_id=product_id,
                                                                 order__isnull=True)
        order_transaction.quantity += int(quantity)
        order_transaction.save()

    return True, 'transaction_created'

