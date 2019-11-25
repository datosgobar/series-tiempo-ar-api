#!coding=utf8
from __future__ import unicode_literals
import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from django_datajsonar.models import Catalog, Node, Distribution
from series_tiempo_ar_api.apps.analytics.models import Query
from series_tiempo_ar_api.apps.management.models import Indicator
from series_tiempo_ar_api.libs.datajsonar_repositories.distribution_repository import DistributionRepository
from series_tiempo_ar_api.libs.indexing.report import attachments
from series_tiempo_ar_api.libs.indexing.report.indicators_generator import IndicatorsGenerator
from series_tiempo_ar_api.libs.indexing.report.node_admins import GlobalAdmins, NodeAdmins
from series_tiempo_ar_api.libs.indexing.report.report_mail_sender import ReportMailSender


class ReportGenerator:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task

    def generate(self):
        self.task.finished = timezone.now()
        self.task.status = self.task.FINISHED
        self.task.save()

        for node in Node.objects.filter(indexable=True):
            IndicatorsGenerator(node, self.task).generate()

        self.generate_email()

        ids = Catalog.objects.all().values_list('identifier')
        # Reportes de catálogo individual
        for node in Node.objects.filter(indexable=True, catalog_id__in=ids):
            self.generate_email(node=node)

    def generate_email(self, node=None):
        """Genera y manda el mail con el reporte de indexación. Si node es especificado, genera el reporte
        con valores de entidades pertenecientes únicamente a ese nodo (reporte individual). Caso contrario
        (default), genera el reporte de indexación global
        """

        context = self.generate_context(node)
        self.send_email(context, node)

    def generate_context(self, node):
        distribution_errors = DistributionRepository.get_all_errored().order_by('dataset__catalog__identifier',
                                                                                'identifier')
        if node:
            distribution_errors = distribution_errors.filter(dataset__catalog__identifier=node.catalog_id)
        context = {
            'distribution_errors': distribution_errors,
            'finish_time': self._format_date(self.task.finished),
            'queries': self.get_queries(),
            'node': node,
        }
        context.update({
            indicator: self._get_indicator_value(indicator, node=node)
            for indicator, _ in Indicator.TYPE_CHOICES
        })
        return context

    def send_email(self, context, node=None):
        start_time = self._format_date(self.task.created)
        subject = self._subject(start_time, node)
        html_msg = render_to_string('indexing/report.html', context=context)
        admins = NodeAdmins(node) if node else GlobalAdmins()

        sender = ReportMailSender(admins=admins, subject=subject, body=html_msg)
        self.add_attachments(sender, node)
        sender.send()

    def _subject(self, start_time, node=None):
        if node is None:
            return f'[{settings.ENV_TYPE}] Validación de series de tiempo: {start_time}'

        return f'[{settings.ENV_TYPE}] Validación de series de tiempo {node.catalog_id}: {start_time}'

    def add_attachments(self, mail_sender, node):
        mail_attachments = (
            ('catalogs.csv', attachments.generate_catalog_attachment(node=node)),
            ('datasets.csv', attachments.generate_dataset_attachment(node=node)),
            ('distributions.csv', attachments.generate_distribution_attachment(node=node)),
            ('series.csv', attachments.generate_field_attachment(node=node)),
        )
        for file_name, body in mail_attachments:
            mail_sender.add_csv_attachment(file_name, body)

        # No se manda si task.logs está vacío
        mail_sender.add_plaintext_attachment('errors.log', self.error_log(node))

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    def _get_indicator_value(self, indicator_type, node=None):
        """Devuelve el valor del indicador_type para el nodo node, o si no es especificado,
        la suma del valor de ese indicador en todos los nodos indexados
        """
        if not indicator_type:
            return 0

        if node:
            indicator_queryset = self.task.indicator_set.filter(type=indicator_type, node=node)
        else:
            indicator_queryset = self.task.indicator_set.filter(type=indicator_type)
        if not indicator_queryset:
            return 0

        return int(sum([indic.value for indic in indicator_queryset]))

    @staticmethod
    def get_queries():
        yesterday = datetime.date.today() - relativedelta(days=1)

        count = Query.objects.filter(timestamp__day=yesterday.day,
                                     timestamp__month=yesterday.month,
                                     timestamp__year=yesterday.year).count()

        return count

    def error_log(self, node=None):
        errored_distributions = DistributionRepository.get_all_errored()
        if node:
            errored_distributions = errored_distributions.filter(
                dataset__catalog__identifier=node.catalog_id)
        errors = errored_distributions.values_list('error_msg', flat=True)
        return "\n\n".join(errors)
