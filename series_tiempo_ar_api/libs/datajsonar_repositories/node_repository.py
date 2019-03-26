from pydatajson import DataJson


class NodeRepository:

    def __init__(self, node):
        self.node = node

    def read_catalog(self):
        return DataJson(self.node.catalog_url)
