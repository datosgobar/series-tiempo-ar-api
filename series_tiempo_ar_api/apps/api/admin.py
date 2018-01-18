from django.contrib import admin

from .models import Catalog, Dataset, Distribution, Field


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'catalog', 'present', 'indexable')
    search_fields = ('identifier', 'catalog__identifier', 'present', 'indexable')
    readonly_fields = ('identifier', 'catalog')
    actions = ['make_indexable', 'make_unindexable']

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no indexable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como indexable'


admin.site.register(Catalog)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Distribution)
admin.site.register(Field)
