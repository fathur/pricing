from django_extensions.db.models import TimeStampedModel


class Model(TimeStampedModel):
    class Meta:
        abstract = True
