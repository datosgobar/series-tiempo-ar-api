from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Catalog, Dataset, Distribution, Field, Query


class QueryAdmin(ModelAdmin):
    list_display = ('timestamp', 'params',)


admin.site.register(Catalog)
admin.site.register(Dataset)
admin.site.register(Distribution)
admin.site.register(Field)
admin.site.register(Query, QueryAdmin)
