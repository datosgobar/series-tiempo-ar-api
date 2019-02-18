from elasticsearch_dsl import DocType, Keyword, Object, Ip, Text, Date, Float, Integer

from series_tiempo_ar_api.apps.analytics.elasticsearch import constants


class SeriesQuery(DocType):

    serie_id = Keyword()
    params = Object()
    ip_address = Ip()
    user_agent = Text()
    timestamp = Date()
    request_time = Float()
    status_code = Integer()

    class Meta:
        index = constants.SERIES_QUERY_INDEX_NAME
