#! coding: utf-8
from elasticsearch.client import IndicesClient, Elasticsearch


class Query:
    """Representa una query de la API de series de tiempo, que termina devolviendo resultados de
    datos leídos de ElasticSearch"""
    def __init__(self, series, query_args):
        """
        Instancia una nueva query
        
        args:
            series (str):  Nombre de una serie
            parameters (dict): Opciones de la query
        """
        self.series = series
        self.args = query_args
        self.elastic = Elasticsearch()
        self.result = {
            'errors': []
        }

    def validate_args(self):
        """Valida los parámetros recibidos"""
        if not self.series:
            self.append_error('No se especificó una serie de tiempo')
            return False

        indices = IndicesClient(client=self.elastic)
        if not indices.exists_type(index="indicators", doc_type=self.series):
            self.append_error('Serie inválida: {}'.format(self.series))
            return False

        return True

    def append_error(self, msg):
        self.result['errors'].append({
            'error': msg
        })
