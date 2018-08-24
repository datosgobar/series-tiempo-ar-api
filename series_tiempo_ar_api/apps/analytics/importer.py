#! coding: utf-8
from urllib import parse

from django.core.exceptions import FieldError
from django.utils import timezone
from iso8601 import iso8601

from series_tiempo_ar_api.apps.analytics.models import AnalyticsImportTask, ImportConfig, Query


class AnalyticsImporter:

    def __init__(self, limit, requests_lib):
        self.requests = requests_lib
        self.limit = limit

        # Precálculo
        self.loaded_api_mgmt_ids = set(Query.objects.values_list('api_mgmt_id', flat=True))

    def run(self, import_all=False):
        task = AnalyticsImportTask(status=AnalyticsImportTask.RUNNING,
                                   timestamp=timezone.now())
        import_config_model = ImportConfig.get_solo()
        task.write_logs("Usando config: endpoint {}, api_id {}, token {}".format(
            import_config_model.endpoint,
            import_config_model.kong_api_id,
            import_config_model.token
        ))
        try:
            self._run_import(import_all)
            task.write_logs("Todo OK")
        except Exception as e:
            task.write_logs("Error importando analytics: {}".format(e))
        task.status = task.FINISHED
        task.save()

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
        self._load_queries_into_db(response)
        next_results = response['next']
        while next_results:
            # Actualizo el cursor en cada iteración en caso de error
            import_config_model.last_cursor = parse.parse_qs(parse.urlsplit(next_results).query)['cursor'][0]
            import_config_model.save()
            response = self.exec_request(url=next_results)
            self._load_queries_into_db(response)
            next_results = response['next']

    def _load_queries_into_db(self, query_results):
        # Filtramos las queries ya agregadas
        ids = self.loaded_api_mgmt_ids
        results = filter(lambda x: x['id'] not in ids, query_results['results'])
        results = filter(lambda x: x['uri'].find('/series/api/') > -1, results)

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

        Query.objects.bulk_create(queries)

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
