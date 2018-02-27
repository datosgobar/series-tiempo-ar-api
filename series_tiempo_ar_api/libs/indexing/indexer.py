#! coding: utf-8
import logging

from django.conf import settings

from . import strings, constants
from .tasks import index_distribution
from .elastic import ElasticInstance

logger = logging.getLogger(__name__)


class Indexer(object):
    """Lee distribuciones y las indexa a través de un bulk create en
    Elasticsearch
    """

    def __init__(self, index=settings.TS_INDEX, async=True):
        self.elastic = ElasticInstance()
        self.index = index
        self.async = async

    def run(self, distributions=None):
        """Indexa en Elasticsearch todos los datos de las
        distribuciones guardadas en la base de datos, o las
        especificadas por el iterable 'distributions'
        """
        self.init_index()

        logger.info(strings.INDEX_START)

        for distribution in distributions:
            if not self.async:
                index_distribution(self.index, distribution.id, async=False)
            else:
                index_distribution.delay(self.index, distribution.id)

        logger.info(strings.INDEX_END)

    def init_index(self):
        if not self.elastic.indices.exists(self.index):
            self.elastic.indices.create(self.index,
                                        body=constants.INDEX_CREATION_BODY)
