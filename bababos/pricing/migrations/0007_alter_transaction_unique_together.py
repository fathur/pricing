# Generated by Django 5.0.2 on 2024-03-03 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0006_transaction_note"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="transaction",
            unique_together={("rfq", "supplier_price")},
        ),
    ]
