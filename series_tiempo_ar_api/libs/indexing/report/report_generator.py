#!coding=utf8
from django.utils import timezone


def generate_report(task):
    """Genera el reporte de indexación de la tarea.

    Args:
        task (ReadDataJsonTask): tarea corrida

    """
    task.finished = timezone.now()
    task.status = task.FINISHED
    task.save()
    task.generate_email()
