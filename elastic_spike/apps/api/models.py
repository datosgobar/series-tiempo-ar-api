#! coding: utf-8
from django.db import models


class Catalog(models.Model):
    title = models.CharField(max_length=2000)
    metadata = models.TextField()


class Dataset(models.Model):
    title = models.CharField(max_length=2000)
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)


class Distribution(models.Model):
    title = models.CharField(max_length=2000)
    metadata = models.TextField()
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField()


class Field(models.Model):
    series_id = models.CharField(max_length=200)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
