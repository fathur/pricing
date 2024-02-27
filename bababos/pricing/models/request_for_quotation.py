import factory
from django.db import models

from bababos.utilities.utils import Model


class RFQ(Model):

    customer = models.ForeignKey(
        to="pricing.Customer", on_delete=models.CASCADE, related_name="RFQs"
    )
    product = models.ForeignKey(
        to="pricing.Product", on_delete=models.CASCADE, related_name="customer_orders"
    )
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=100)

    class Meta:
        db_table = "request_for_quotations"


class RFQFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RFQ
