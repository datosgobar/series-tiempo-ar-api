from series_tiempo_ar import TimeSeriesDataJson


class NodeRepository:

    def __init__(self, node):
        self.node = node

    def read_catalog(self):
        return TimeSeriesDataJson(self.node.catalog_url)
