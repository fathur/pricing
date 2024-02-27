import factory
from django.db import models

from bababos.utilities.utils import Model


class SupplierPrice(Model):

    supplier = models.ForeignKey(
        to="pricing.Supplier", on_delete=models.CASCADE, related_name="prices"
    )
    product = models.ForeignKey(
        to="pricing.Product", on_delete=models.CASCADE, related_name="supplier_prices"
    )
    price = models.DecimalField(
        max_digits=21, decimal_places=5
    )  # 1_000_000_000_000_000,00000
    available_stock = models.IntegerField(default=0)
    latest = models.BooleanField(default=True)

    class Meta:
        db_table = "supplier_prices"


class SupplierPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupplierPrice
