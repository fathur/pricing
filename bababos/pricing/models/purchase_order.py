import factory
from django.db import models
from django.utils import timezone
from faker import Faker

from bababos.utilities.utils import Model

fake = Faker()


class PO(Model):

    customer = models.ForeignKey(
        to="pricing.Customer", on_delete=models.CASCADE, related_name="POs"
    )
    product = models.ForeignKey(to="pricing.Product", on_delete=models.CASCADE)
    ordered_at = models.DateTimeField()
    quantity = models.IntegerField()
    unit = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=21, decimal_places=5, db_comment="Unit selling price"
    )

    class Meta:
        db_table = "purchase_orders"

    @property
    def total(self):
        return self.quantity * self.price


class POFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PO

    ordered_at = factory.LazyAttribute(
        lambda _: timezone.make_aware(fake.date_time_between())
    )
