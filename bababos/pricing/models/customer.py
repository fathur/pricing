import factory
from django.contrib.auth.models import User
from django.db import models

from bababos.utilities.utils import Model


class Customer(Model):

    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, related_name="customer"
    )
    code = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    region = models.ForeignKey(
        "pricing.Region", on_delete=models.CASCADE, related_name="customers"
    )

    class Meta:
        db_table = "customers"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("first_name")


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)
    region = factory.SubFactory("bababos.pricing.models.RegionFactory")
