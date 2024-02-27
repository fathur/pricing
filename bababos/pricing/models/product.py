import factory
from django.db import models

from bababos.utilities.utils import Model


class Product(Model):

    sku = models.CharField(max_length=100, unique=True, db_comment="Stock keeping unit")
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "products"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
