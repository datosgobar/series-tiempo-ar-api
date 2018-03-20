#!coding=utf8
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from pydatajson import DataJson

from series_tiempo_ar_api.apps.management.models import Indicator, Node
from series_tiempo_ar_api.apps.api.models import Catalog, Dataset, Field, Distribution
from series_tiempo_ar_api.libs.indexing.report.indicators import IndicatorLoader


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task
        self.indicators_loader = IndicatorLoader()

    def generate(self):
        self.task.finished = timezone.now()
        self.task.status = self.task.FINISHED
        self.task.save()
        self.persist_indicators()
        self.calculate_indicators()
        self.generate_email()
        self.indicators_loader.clear_indicators()

    def generate_email(self):
        start_time = self._format_date(self.task.created)
        finish_time = self._format_date(self.task.finished)
        msg = "Horario de finalización: {}\n".format(finish_time)

        msg += self.format_message(
            'Catálogos',
            {
                'new': Indicator.CATALOG_NEW,
                'updated': Indicator.CATALOG_UPDATED,
                'total': Indicator.CATALOG_TOTAL,
                'not_updated': Indicator.CATALOG_NOT_UPDATED,
            })
        msg += self.format_message(
            'Datasets',
            {
                'new': Indicator.DATASET_NEW,
                'updated': Indicator.DATASET_UPDATED,
                'total': Indicator.DATASET_TOTAL,
                'not_updated': Indicator.DATASET_NOT_UPDATED,
                'indexable': Indicator.DATASET_INDEXABLE,
                'not_indexable': Indicator.DATASET_NOT_INDEXABLE,
                'error': Indicator.DATASET_ERROR,
            })
        msg += self.format_message(
            'Distribuciones',
            {
                'new': Indicator.DISTRIBUTION_NEW,
                'updated': Indicator.DISTRIBUTION_UPDATED,
                'total': Indicator.DISTRIBUTION_TOTAL,
                'not_updated': Indicator.DISTRIBUTION_NOT_UPDATED,
                'indexable': Indicator.DISTRIBUTION_INDEXABLE,
                'not_indexable': Indicator.DISTRIBUTION_NOT_INDEXABLE,
                'error': Indicator.DISTRIBUTION_ERROR,
            })
        msg += self.format_message(
            'Series',
            {
                'new': Indicator.FIELD_NEW,
                'updated': Indicator.FIELD_UPDATED,
                'not_updated': Indicator.FIELD_NOT_UPDATED,
                'indexable': Indicator.FIELD_INDEXABLE,
                'not_indexable': Indicator.FIELD_NOT_INDEXABLE,
                'error': Indicator.FIELD_ERROR,
                'total': Indicator.FIELD_TOTAL,
            })
        recipients = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP)
        emails = [user.email for user in recipients.user_set.all()]
        subject = u'[{}] API Series de Tiempo: {}'.format(settings.ENV_TYPE, start_time)

        sent = send_mail(subject, msg, settings.EMAIL_HOST_USER, emails)
        if emails and not sent:
            raise ValueError

    def format_message(self, full_name, indicators):
        context = indicators.copy()

        for name, indicator in context.iteritems():
            context[name] = self._get_indicator_value(indicator)

        context['name'] = full_name
        msg = render_to_string('indexing/report.txt', context=context)
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

        nodes = Node.objects.filter(indexable=True)
        catalog_ids = nodes.values_list('catalog_id', flat=True)
        for catalog_model in Catalog.objects.filter(identifier__in=catalog_ids):
            node = nodes.get(catalog_id=catalog_model.identifier)

            self.calculate_catalog_indicators(node)
            data_json = DataJson(json.loads(node.catalog))

            self.calculate_series_indicators(node, data_json)
            self.calculate_distribution_indicators(node, data_json)
            self.calculate_dataset_indicators(node, data_json)

    def calculate_catalog_indicators(self, node):
        catalog_model = Catalog.objects.get(identifier=node.catalog_id)
        updated = catalog_model.updated
        self.task.indicator_set.create(type=Indicator.CATALOG_UPDATED, value=updated, node=node)
        not_updated = 1 - updated
        self.task.indicator_set.create(type=Indicator.CATALOG_NOT_UPDATED, value=not_updated,
                                       node=node)
        self.task.indicator_set.create(type=Indicator.CATALOG_TOTAL, value=1, node=node)

    def calculate_series_indicators(self, node, data_json):
        fields_total = len(data_json.get_fields(only_time_series=True))
        self.task.indicator_set.create(type=Indicator.FIELD_TOTAL, value=fields_total, node=node)

        catalog = Catalog.objects.get(identifier=node.catalog_id)
        total = self.task.indicator_set.filter(type=Indicator.FIELD_TOTAL)
        total = total[0].value if total else 0

        indexable = Field.objects.filter(distribution__dataset__catalog=catalog,
                                         distribution__dataset__indexable=True).count()
        self.task.indicator_set.create(type=Indicator.FIELD_INDEXABLE, value=indexable, node=node)

        not_indexable = total - indexable
        self.task.indicator_set.create(type=Indicator.FIELD_NOT_INDEXABLE, value=not_indexable, node=node)
        updated = self.task.indicator_set.get_or_create(type=Indicator.FIELD_UPDATED, node=node)[0].value

        not_updated = indexable - updated
        self.task.indicator_set.create(type=Indicator.FIELD_NOT_UPDATED, value=not_updated, node=node)

    def calculate_distribution_indicators(self, node, data_json):
        distribution_total = len(data_json.get_distributions(only_time_series=True))
        self.task.indicator_set.create(type=Indicator.DISTRIBUTION_TOTAL,
                                       value=distribution_total,
                                       node=node)

        catalog = Catalog.objects.get(identifier=node.catalog_id)
        total = self.task.indicator_set.filter(type=Indicator.DISTRIBUTION_TOTAL)
        total = total[0].value if total else 0

        indexable = Distribution.objects.filter(dataset__catalog=catalog,
                                                dataset__indexable=True).count()
        self.task.indicator_set.create(type=Indicator.DISTRIBUTION_INDEXABLE, value=indexable, node=node)
        not_indexable = total - indexable
        self.task.indicator_set.create(type=Indicator.DISTRIBUTION_NOT_INDEXABLE, value=not_indexable, node=node)

        updated = self.task.indicator_set.get_or_create(type=Indicator.DISTRIBUTION_UPDATED, node=node)[0].value

        not_updated = indexable - updated
        self.task.indicator_set.create(type=Indicator.DISTRIBUTION_NOT_UPDATED, value=not_updated, node=node)

    def calculate_dataset_indicators(self, node, data_json):
        dataset_total = len(data_json.get_datasets(only_time_series=True))
        self.task.indicator_set.create(type=Indicator.DATASET_TOTAL, value=dataset_total, node=node)

        catalog = Catalog.objects.get(identifier=node.catalog_id)
        total = self.task.indicator_set.filter(type=Indicator.DATASET_TOTAL)
        total = total[0].value if total else 0

        indexable = Dataset.objects.filter(catalog=catalog, indexable=True).count()
        self.task.indicator_set.create(type=Indicator.DATASET_INDEXABLE, value=indexable, node=node)

        not_indexable = total - indexable
        self.task.indicator_set.create(type=Indicator.DATASET_NOT_INDEXABLE, value=not_indexable, node=node)
        updated = self.task.indicator_set.get_or_create(type=Indicator.DATASET_UPDATED, node=node)[0].value

        not_updated = indexable - updated
        self.task.indicator_set.create(type=Indicator.DATASET_NOT_UPDATED, value=not_updated, node=node)

        error = Dataset.objects.filter(catalog=catalog, error=True).count()
        self.task.indicator_set.create(type=Indicator.DATASET_ERROR, value=error, node=node)

    def persist_indicators(self):
        self.indicators_loader.load_indicators_into_db(self.task)
