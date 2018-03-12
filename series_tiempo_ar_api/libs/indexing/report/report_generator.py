#!coding=utf8
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.utils import timezone
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Indicator, Node
from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Field
from . import strings


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task

    def generate(self):
        self.task.finished = timezone.now()
        self.task.status = self.task.FINISHED
        self.task.save()
        self.calculate_indicators()
        self.generate_email()

    def generate_email(self):
        start_time = self._format_date(self.task.created)
        finish_time = self._format_date(self.task.finished)
        msg = "Horario de finalización: {}\n".format(finish_time)

        msg += self.format_message('Catálogos',
                                   Indicator.CATALOG_NEW,
                                   Indicator.CATALOG_UPDATED,
                                   Indicator.CATALOG_TOTAL,
                                   None, None, None, None)
        msg += self.format_message('Datasets',
                                   Indicator.DATASET_NEW,
                                   Indicator.DATASET_UPDATED,
                                   Indicator.DATASET_TOTAL,
                                   None, None, None, None)
        msg += self.format_message('Distribuciones',
                                   Indicator.DISTRIBUTION_NEW,
                                   Indicator.DISTRIBUTION_UPDATED,
                                   Indicator.DISTRIBUTION_TOTAL,
                                   None, None, None, None)
        msg += self.format_message('Series',
                                   Indicator.FIELD_NEW,
                                   Indicator.FIELD_UPDATED,
                                   Indicator.FIELD_TOTAL,
                                   Indicator.FIELD_NOT_UPDATED,
                                   Indicator.FIELD_INDEXABLE,
                                   Indicator.FIELD_NOT_INDEXABLE,
                                   Indicator.FIELD_ERROR)

        recipients = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP)
        emails = [user.email for user in recipients.user_set.all()]
        subject = u'[{}] API Series de Tiempo: {}'.format(settings.ENV_TYPE, start_time)

        sent = send_mail(subject, msg, settings.EMAIL_HOST_USER, emails)
        if emails and not sent:
            raise ValueError

    def format_message(self, full_name,
                       new_indicator, updated_indicator, total_indicator,
                       not_updated_indicator, indexable, not_indexable, error):
        new_value = self._get_indicator_value(new_indicator)
        updated_value = self._get_indicator_value(updated_indicator)
        not_updated_value = self._get_indicator_value(not_updated_indicator)
        indexable_value = self._get_indicator_value(indexable)
        not_indexable_value = self._get_indicator_value(not_indexable)
        total_value = self._get_indicator_value(total_indicator)
        error_value = self._get_indicator_value(error)

        msg = strings.INDEXING_REPORT_TEMPLATE.format(name=full_name,
                                                      new=new_value,
                                                      updated=updated_value,
                                                      not_updated=not_updated_value,
                                                      indexable=indexable_value,
                                                      not_indexable=not_indexable_value,
                                                      error=error_value,
                                                      total=total_value)
        return msg

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    def _get_indicator_value(self, indicator_type):
        if not indicator_type:
            return 0

        indicator_queryset = self.task.indicator_set.filter(type=indicator_type)
        if not indicator_queryset:
            return 0

        return sum([indic.value for indic in indicator_queryset])

    def calculate_indicators(self):
        for node in Node.objects.filter(indexable=True):
            catalog = Catalog.objects.filter(identifier=node.catalog_id)
            if not catalog:
                continue

            catalog = catalog[0]

            dataset_total = Dataset.objects.filter(catalog__identifier=node.catalog_id, present=True).count()
            self.task.indicator_set.create(type=Indicator.DATASET_TOTAL, value=dataset_total, node=node)

            dataset_updated = Dataset.objects.filter(catalog__identifier=node.catalog_id, updated=True).count()
            self.task.indicator_set.create(type=Indicator.DATASET_UPDATED, value=dataset_updated, node=node)

            self.task.indicator_set.create(type=Indicator.CATALOG_TOTAL, value=1, node=node)
            self.task.indicator_set.create(type=Indicator.CATALOG_UPDATED, value=int(catalog.updated), node=node)

            data_json = DataJson(json.loads(node.catalog))
            fields_total = len(data_json.get_fields(only_time_series=True))
            self.task.indicator_set.create(type=Indicator.FIELD_TOTAL, value=fields_total, node=node)
            self.calculate_series_indicators(node)

    def calculate_series_indicators(self, node):
        catalog = Catalog.objects.get(identifier=node.catalog_id)
        total = self.task.indicator_set.filter(type=Indicator.FIELD_TOTAL)
        total = total[0].value if total else 0

        updated = Field.objects.filter(distribution__dataset__catalog=catalog, updated=True).count()
        self.task.indicator_set.create(type=Indicator.FIELD_UPDATED, value=updated, node=node)

        not_updated = total - updated
        self.task.indicator_set.create(type=Indicator.FIELD_NOT_UPDATED, value=not_updated, node=node)

        indexable = Field.objects.filter(distribution__dataset__catalog=catalog,
                                         distribution__dataset__indexable=True).count()
        self.task.indicator_set.create(type=Indicator.FIELD_INDEXABLE, value=indexable, node=node)

        not_indexable = total - indexable
        self.task.indicator_set.create(type=Indicator.FIELD_NOT_INDEXABLE, value=not_indexable, node=node)
