import csv
from io import StringIO, BytesIO

import pandas as pd
from des.models import DynamicEmailConfiguration
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.test import Client
from django.urls import reverse
from django_rq import job

from scripts.integration_test import IntegrationTest
from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management.models import IntegrationTestTask, IntegrationTestConfig
from series_tiempo_ar_api.libs.indexing.api_index_enqueue import enqueue_job_with_timeout


class DjangoSeriesFetcher:

    def __init__(self):
        self.client = Client()

    def fetch(self, series_id, **kwargs):
        data = {'ids': series_id, 'format': 'csv'}
        data.update(kwargs)
        response = self.client.get(reverse('api:series:series'), data=data)

        if response.status_code != 200:
            return None

        out_stream = StringIO(str(response.content, encoding='utf8'))

        return pd.read_csv(out_stream, parse_dates=['indice_tiempo'], index_col='indice_tiempo')

    def get_url(self, serie_id: str):
        endpoint = IntegrationTestConfig.get_solo().api_endpoint
        return f'{endpoint}?ids={serie_id}&last=1000&format=csv'


@job("integration_test", timeout=-1)
def run_integration(task: IntegrationTestTask = None):
    task = task or IntegrationTestTask.objects.create()

    metadata = DumpFile.objects.filter(node=None,
                                       file_type=DumpFile.TYPE_CSV,
                                       file_name=DumpFile.FILENAME_METADATA).last()

    if not metadata:
        task.log("No se encontró un dump de metadatos generado en la aplicación.")
        task.refresh_from_db()
        task.status = IntegrationTestTask.FINISHED
        task.save()

    series_metadata = pd.read_csv(BytesIO(metadata.file.read()), index_col='serie_id')
    setattr(settings, "ALLOWED_HOSTS", ["*"])

    result = IntegrationTest(series_metadata=series_metadata,
                             fetcher=DjangoSeriesFetcher()).test()

    task.log(str(result))

    if result:
        send_email(result, task)

    task.refresh_from_db()
    task.status = IntegrationTestTask.FINISHED
    task.save()


def send_email(result: list, task: IntegrationTestTask):
    subject = u'[{}] API Series de Tiempo: Test de integración'.format(settings.ENV_TYPE)
    emails = IntegrationTestConfig.get_solo().recipients.values_list('email', flat=True)
    if not emails:
        task.log("No hay usuarios registrados para recibir los reportes del test. Mail no enviado.")
        return

    msg = "Errores en los datos de las series detectados. Ver el archivo adjunto"
    config = DynamicEmailConfiguration.get_solo()
    mail = EmailMultiAlternatives(subject, msg, from_email=config.from_email, to=emails)
    mail.attach('errors.csv', generate_errors_csv(result), 'text/csv')
    sent = mail.send()
    if not sent:
        task.log("Error mandando el reporte")


def generate_errors_csv(result: list):
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=["serie_id", "error_pct", "api_url", "distribution_url"])
    writer.writeheader()
    writer.writerows(result)
    out.seek(0)
    return out.read()


@job("integration_test")
def enqueue_new_integration_test(*_):
    timeout = IntegrationTestConfig.get_solo().timeout
    enqueue_job_with_timeout('integration_test', run_integration, timeout)
