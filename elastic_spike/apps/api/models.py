from django.db import models


class Catalog(models.Model):
    metadata = models.TextField()


class Dataset(models.Model):
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)


class Distribution(models.Model):
    metadata = models.TextField()
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField()


class Field(models.Model):
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
