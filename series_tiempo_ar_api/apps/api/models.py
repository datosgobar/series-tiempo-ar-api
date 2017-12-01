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
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'%s' % (self.series_id)


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ids = models.CharField(max_length=2000)
    args = models.CharField(max_length=2000)
    timestamp = models.DateTimeField()
    ip_address = models.CharField(max_length=200, null=True)
    params = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.timestamp = timezone.now()
        super(Query, self).save(force_insert, force_update, using, update_fields)
