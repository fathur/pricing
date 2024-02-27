import factory
from django.db import models

from bababos.utilities.utils import Model


class Quotation(Model):

    RFQ = models.OneToOneField(to="pricing.RFQ", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=21, decimal_places=5, db_comment="Price per item"
    )

    class Meta:
        db_table = "quotations"


class QuotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quotation
