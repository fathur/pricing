import factory
from django.contrib.auth.models import User
from django.db import models
from softdelete.models import SoftDeleteObject

from bababos.pricing.models.customer import UserFactory
from bababos.utilities.utils import Model


class Supplier(SoftDeleteObject, Model):

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    region = models.ForeignKey(to="pricing.Region", on_delete=models.CASCADE)

    class Meta:
        db_table = "suppliers"


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    code = factory.Faker("last_name")
    user = factory.SubFactory(UserFactory)
    region = factory.SubFactory("bababos.pricing.models.RegionFactory")
