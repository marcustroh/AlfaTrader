# Generated by Django 5.1.3 on 2025-01-10 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AlfaTrader_App', '0012_alter_fees_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fees',
            name='transaction_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='AlfaTrader_App.transactions'),
        ),
    ]
