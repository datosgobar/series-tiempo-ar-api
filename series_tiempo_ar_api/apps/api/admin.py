from django.contrib import admin

from .models import Catalog, Dataset, Distribution, Field


admin.site.register(Catalog)
admin.site.register(Dataset)
admin.site.register(Distribution)
admin.site.register(Field)
