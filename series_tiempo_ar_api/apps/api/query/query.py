#! coding: utf-8
from series_tiempo_ar_api.apps.api.query.es_query import ESQuery, CollapseQuery


class Query(object):
    """Encapsula la query pedida por un usuario. Tiene dos componentes
    principales: la parte de datos obtenida haciendo llamadas a
    Elasticsearch, y los metadatos guardados en la base de datos
    relacional
    """
    def __init__(self):
        self.es_query = ESQuery()
        self.meta = {}
        self.metadata_config = None

    def get_series_ids(self):
        return self.es_query.get_series_ids()

    def add_pagination(self, start, limit):
        return self.es_query.add_pagination(start, limit)

    def add_filter(self, start_date, end_date):
        return self.es_query.add_filter(start_date, end_date)

    def add_series(self, name, rep_mode):
        return self.es_query.add_series(name, rep_mode)

    def add_collapse(self, agg, collapse, rep_mode):
        self.es_query = CollapseQuery(self.es_query)
        return self.es_query.add_collapse(agg, collapse, rep_mode)

    def set_metadata_config(self, how):
        self.metadata_config = how
