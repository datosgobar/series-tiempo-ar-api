from django.contrib import admin
from django.db.models import Q

from django_datajsonar.admin.data_json import FieldAdmin, DistributionAdmin
from django_datajsonar.models import Field, Distribution

from .utils import delete_metadata
from .tasks import reindex_distribution

admin.site.unregister(Field)
admin.site.unregister(Distribution)


@admin.register(Field)
class CustomFieldAdmin(FieldAdmin):
    actions = ('delete_model',)

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(CustomFieldAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, _, queryset):
        delete_fields(queryset)
        queryset.delete()


@admin.register(Distribution)
class CustomDistributionAdmin(DistributionAdmin):
    actions = ('delete_model', 'reindex')

    def get_actions(self, request):
        # Borro la acción de borrado default
        actions = super(CustomDistributionAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_model(self, _, queryset):
        fields = Field.objects.filter(distribution__identifier__in=queryset.values_list('identifier', flat=True))
        if not fields:
            return
        delete_fields(fields)
        queryset.delete()

    def reindex(self, _, queryset):
        for distribution in queryset:
            reindex_distribution.delay(distribution)
    reindex.short_description = "Refrescar datos"


def delete_fields(queryset):
    delete_metadata(list(queryset.filter(~Q(identifier=None))))
