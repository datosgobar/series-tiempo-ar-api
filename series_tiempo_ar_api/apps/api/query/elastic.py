#! coding: utf-8
from elasticsearch import Elasticsearch
from series_tiempo_ar_api.apps.api.query import strings


class ElasticInstance(object):
    elastic = None

    @classmethod
    def init(cls, urls, options=None):
        """
        Devuelve la instancia del cliente de Elasticsearch. Si se
        espeficica el parámetro 'urls', inicializa un cliente nuevo con
        conexión a las instancias en esas direcciones.

        Args:
            urls (list): Lista de URLs a conectarse
            options (dict): Opciones para configurar el cliente Elasticsearch

        Returns:
            Elasticsearch
        """
        if cls.elastic:
            return cls.elastic
        if options is None:
            options = {}
        cls.elastic = Elasticsearch(urls, **options)
        return cls.elastic

    @classmethod
    def get(cls):
        if cls.elastic is None:
            raise NotInitializedError

        return cls.elastic

    def __new__(cls):
        return cls.get()


class NotInitializedError(BaseException):
    message = strings.ES_NOT_INIT_ERROR
