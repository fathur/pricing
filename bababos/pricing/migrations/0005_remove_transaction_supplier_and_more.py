# Generated by Django 5.0.2 on 2024-03-03 06:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0004_supplierprice_latest"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="supplier",
        ),
        migrations.AddField(
            model_name="transaction",
            name="supplier_price",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="pricing.supplierprice",
            ),
            preserve_default=False,
        ),
    ]
