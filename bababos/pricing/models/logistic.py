import factory
from django.db import models

from bababos.utilities.utils import Model


class Logistic(Model):

    fleet_type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    class Meta:
        db_table = "logistics"


class LogisticFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Logistic
