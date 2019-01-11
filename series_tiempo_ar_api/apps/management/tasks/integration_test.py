import csv
from io import StringIO, BytesIO

import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMultiAlternatives
from django.test import Client
from django.urls import reverse
from django_rq import job

from scripts.integration_test import IntegrationTest
from series_tiempo_ar_api.apps.dump.models import DumpFile
from series_tiempo_ar_api.apps.management.models import IntegrationTestTask


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


@job("default", timeout=-1)
def run_integration(task: IntegrationTestTask):
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

    if len(result):
        send_email(result, task)

    task.refresh_from_db()
    task.status = IntegrationTestTask.FINISHED
    task.save()


def send_email(result: list, task: IntegrationTestTask):
    subject = u'[{}] API Series de Tiempo: Test de integración'.format(settings.ENV_TYPE)
    emails = Group.objects.get(name=settings.INTEGRATION_TEST_REPORT_GROUP).user_set.values_list('email', flat=True)
    if not emails:
        task.log("No hay usuarios registrados para recibir los reportes del test. Mail no enviado.")
        return

    msg = "Errores en los datos de las series detectados. Ver el archivo adjunto"
    mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
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
