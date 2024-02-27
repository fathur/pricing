import factory
from django.db import models

from bababos.utilities.utils import Model


class LogisticPrice(Model):

    logistic = models.ForeignKey(
        to="pricing.Logistic", on_delete=models.CASCADE, related_name="prices"
    )
    source = models.ForeignKey(
        to="pricing.Region",
        on_delete=models.CASCADE,
        related_name="logistic_price_sources",
    )
    destination = models.ForeignKey(
        to="pricing.Region",
        on_delete=models.CASCADE,
        related_name="logistic_price_destinations",
    )
    price = models.DecimalField(
        max_digits=21, decimal_places=5
    )  # 1_000_000_000_000_000,00000

    class Meta:
        db_table = "logistic_prices"
        unique_together = "logistic", "source", "destination"


class LogisticPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LogisticPrice
