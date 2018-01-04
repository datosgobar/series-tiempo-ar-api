# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .bulk_index import bulk_index
from .models import DatasetIndexingFile


class DatasetsIndexingFileAdmin(admin.ModelAdmin):
    actions = ['run']

    readonly_fields = ('created', 'modified', 'state', 'logs')

    def run(self, _, queryset):
        for model in queryset:
            model.state = DatasetIndexingFile.state = DatasetIndexingFile.PROCESSING
            model.logs = u'-'
            model.save()
            bulk_index.delay(model.id)

    run.short_description = 'Ejecutar'

    def get_form(self, request, obj=None, **kwargs):
        form = super(DatasetsIndexingFileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['uploader'].initial = request.user
        return form

    def save_form(self, request, form, change):
        return super(DatasetsIndexingFileAdmin, self).save_form(request, form, change)


admin.site.register(DatasetIndexingFile, DatasetsIndexingFileAdmin)
