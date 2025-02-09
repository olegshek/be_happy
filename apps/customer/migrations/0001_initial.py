# Generated by Django 3.0.8 on 2020-08-02 08:08

import apps.customer.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(blank=True, max_length=20, null=True)),
                ('full_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Full name')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Phone number')),
                ('language', models.CharField(choices=[('ru', 'Russian'), ('uz', 'Uzbek'), ('en', 'English')], default='ru', max_length=2, verbose_name='Language')),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.CharField(blank=True, max_length=50, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, max_length=50, null=True, verbose_name='Longitude')),
                ('address', models.TextField(null=True, verbose_name='Address')),
                ('distance', models.FloatField(default=0.0, verbose_name='Distance')),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order_id', models.IntegerField(default=apps.customer.models._generate_order_id, verbose_name='Order id')),
                ('order_type', models.CharField(choices=[('DELIVERY', '🚘 Delivery'), ('PICKUP', '🏃 Pickup')], default='DELIVERY', max_length=8, verbose_name='Order type')),
                ('order_time', models.TimeField(null=True, verbose_name='Order time')),
                ('confirmed_at', models.DateTimeField(blank=True, null=True, verbose_name='Confirmed at')),
                ('status', models.CharField(choices=[('ACCEPTED', 'ACCEPTED'), ('EN ROUTE', 'EN ROUTE'), ('DELIVERED', 'DELIVERED'), ('PENDING', 'PENDING'), ('COOKING', 'COOKING'), ('CANCELLED', 'CANCELLED')], default='PENDING', max_length=40, verbose_name='Status')),
                ('payment_type', models.CharField(choices=[('CASH', '💵 Cash'), ('PAYME', '💳 Payme')], max_length=10, null=True, verbose_name='Payment type')),
                ('paid_at', models.DateTimeField(null=True, verbose_name='Paid at')),
                ('delivery_price', models.IntegerField(default=0, verbose_name='Delivery price')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='customer.Customer', verbose_name='Customer')),
                ('location', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='customer.Location', verbose_name='Location')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ('-confirmed_at', '-order_id'),
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0, verbose_name='Quantity')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='customer.Customer', verbose_name='Customer')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='customer.Order', verbose_name='Order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='store.Product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='ReviewMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('message', models.TextField(verbose_name='Message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_messages', to='customer.Customer', verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Review message',
                'verbose_name_plural': 'Review messages',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CustomerActivityEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=200)),
                ('data', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_events', to='customer.Customer')),
            ],
        ),
    ]
