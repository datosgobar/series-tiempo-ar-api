#! coding: utf-8
from elasticsearch import Elasticsearch


class ElasticInstance(object):

    elastic = Elasticsearch()

    @classmethod
    def get(cls, urls=None):
        """Devuelve la instancia del cliente de Elasticsearch. Si se
        espeficica el parámetro 'urls', inicializa un cliente nuevo con
        conexión a las instancias en esas direcciones.
        
        Args:
            urls (list): Lista de URLs a conectarse
            
        Returns:
            Elasticsearch
        """
        if not urls:
            return cls.elastic
        cls.elastic = Elasticsearch(urls)
        return cls.elastic
