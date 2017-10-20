#! coding: utf-8
from elasticsearch import Elasticsearch


class ElasticInstance(object):

    elastic = None

    @classmethod
    def init(cls, urls):
        """Devuelve la instancia del cliente de Elasticsearch. Si se
        espeficica el parámetro 'urls', inicializa un cliente nuevo con
        conexión a las instancias en esas direcciones.

        Args:
            urls (list): Lista de URLs a conectarse

        Returns:
            Elasticsearch
        """
        if cls.elastic:
            return cls.elastic

        cls.elastic = Elasticsearch(urls)
        return cls.elastic

    @classmethod
    def get(cls):
        if cls.elastic is None:
            raise NotInitializedError

        return cls.elastic

    def __new__(cls, *args, **kwargs):
        return cls.get()


class NotInitializedError(BaseException):
    message = "Instancia no inicializada. Pruebe con init(urls)"
