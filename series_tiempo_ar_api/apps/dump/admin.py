#!coding=utf8
from django.contrib import admin
from .models import CSVDumpTask


class CSVDumpAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs')


admin.site.register(CSVDumpTask, CSVDumpAdmin)
