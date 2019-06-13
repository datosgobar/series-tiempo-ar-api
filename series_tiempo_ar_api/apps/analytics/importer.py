#! coding: utf-8
from urllib import parse

import requests
from django.core.exceptions import FieldError
from iso8601 import iso8601

from series_tiempo_ar_api.apps.analytics.elasticsearch.index import AnalyticsIndexer
from series_tiempo_ar_api.apps.analytics.models import AnalyticsImportTask, ImportConfig, Query


class AnalyticsImporter:

    def __init__(self, task=None, limit=1000, requests_lib=requests, index_to_es=True):
        self.task = task or AnalyticsImportTask.objects.create()
        self.requests = requests_lib
        self.limit = limit
        self.index_to_es = index_to_es

        # Precálculo
        self.loaded_api_mgmt_ids = set(Query.objects.values_list('api_mgmt_id', flat=True))

    def run(self, import_all=False):
        import_config_model = ImportConfig.get_solo()
        AnalyticsImportTask.info(self.task, "Usando config: endpoint {}, api_id {}, token {}".format(
            import_config_model.endpoint,
            import_config_model.kong_api_id,
            import_config_model.token
        ))
        try:
            self._run_import(import_all)
            AnalyticsImportTask.info(self.task, "Todo OK")
        except Exception as e:
            AnalyticsImportTask.info(self.task, "Error importando analytics: {}".format(e))
            raise e

        self.task.refresh_from_db()
        self.task.status = AnalyticsImportTask.FINISHED
        self.task.save()

    def _run_import(self, import_all=False):
        import_config_model = ImportConfig.get_solo()
        if (not import_config_model.endpoint or
                not import_config_model.token or
                not import_config_model.kong_api_id):
            raise FieldError("Configuración de importación de analytics no inicializada")

        cursor = import_config_model.last_cursor or None
        if import_all:
            cursor = None

        response = self.exec_request(cursor=cursor,
                                     kong_api_id=import_config_model.kong_api_id)
        self._load_queries(response)
        next_results = response['next']
        while next_results:
            # Actualizo el cursor en cada iteración en caso de error
            import_config_model.last_cursor = parse.parse_qs(parse.urlsplit(next_results).query)['cursor'][0]
            import_config_model.save()
            response = self.exec_request(url=next_results)
            self._load_queries(response)
            next_results = response['next']

    def _load_queries(self, response):
        queries = self.create_queries(response)
        # A db
        Query.objects.bulk_create(queries)
        # a ES
        if self.index_to_es:
            queries = Query.objects.filter(api_mgmt_id__in=[q.api_mgmt_id for q in queries])
            AnalyticsIndexer().index(queries)

    def exec_request(self, url=None, **params):
        """Wrapper sobre la llamada a la API de api-mgmt"""
        if url and params:
            raise ValueError

        import_config_model = ImportConfig.get_solo()

        if url is None:
            url = import_config_model.endpoint

        return self.requests.get(
            url,
            headers=import_config_model.get_authorization_header(),
            params=params,
        ).json()

    def create_queries(self, query_results):
        # Filtramos las queries ya agregadas
        ids = self.loaded_api_mgmt_ids
        results = filter(lambda x: x['id'] not in ids, query_results['results'])
        results = filter(lambda x: x['uri'].find('/series/api/') > -1, results)
        results = filter(lambda x: x['request_method'] != 'OPTIONS', results)

        queries = []
        for result in results:
            parsed_querystring = parse.parse_qs(result['querystring'], keep_blank_values=True)
            queries.append(Query(
                ip_address=result['ip_address'],
                args=result['querystring'],
                timestamp=iso8601.parse_date(result['start_time']),
                ids=parsed_querystring.get('ids', ''),
                params=parsed_querystring,
                api_mgmt_id=result['id'],
                uri=result.get('uri') or '',
                request_time=result.get('request_time') or 0,
                user_agent=result.get('user_agent') or '',
                status_code=result.get('status_code') or 0,
            ))
            self.loaded_api_mgmt_ids.update([result['id']])

        return queries
