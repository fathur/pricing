import factory
from django.db import models
from django_extensions.db.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Region(MPTTModel, TimeStampedModel):

    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        db_table = "regions"


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region
