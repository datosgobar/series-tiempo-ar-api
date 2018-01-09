#! coding: utf-8
from django.utils import timezone
from django.db import models


class Catalog(models.Model):
    title = models.CharField(max_length=2000)
    identifier = models.CharField(max_length=200, default='sspm', unique=True)
    metadata = models.TextField()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.identifier)


class Dataset(models.Model):
    identifier = models.CharField(max_length=200)
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)
    indexable = models.BooleanField(default=False)
    present = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.catalog.identifier)


def filepath(instance, _):
    """Método para asignar el nombre al archivo fuente del FileField
    del modelo Distribution
    """
    return u'distribution_raw/{}.csv'.format(instance.identifier)


class Distribution(models.Model):
    identifier = models.CharField(max_length=200)
    metadata = models.TextField()
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField(max_length=1024)
    periodicity = models.CharField(max_length=200)

    data_file = models.FileField(
        max_length=2000,
        upload_to=filepath,
        blank=True
    )

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)


class Field(models.Model):
    series_id = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'%s' % (self.series_id)
