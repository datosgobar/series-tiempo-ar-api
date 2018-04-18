#! coding: utf-8
import unicodecsv
import yaml

from series_tiempo_ar_api.apps.api.models import Catalog, Dataset
from .models import Node, NodeRegisterFile
from .strings import DATASET_STATUS

CATALOG_HEADER = u'catalog_id'
DATASET_ID_HEADER = u'dataset_identifier'


class DatasetIndexableToggler(object):

    def __init__(self):
        self.logs = []
        self.catalogs = {}

    def process(self, federation_file):
        self.read_dataset_csv(federation_file)
        self.update_database()
        return self.logs

    def read_dataset_csv(self, federation_file):
        reader = unicodecsv.reader(federation_file)

        headers = next(reader)
        if CATALOG_HEADER not in headers or DATASET_ID_HEADER not in headers:
            raise ValueError

        catalog_idx = headers.index(CATALOG_HEADER)
        dataset_id_idx = headers.index(DATASET_ID_HEADER)

        # Struct con catalog identifiers como keys y listas de datasets como values
        for line in reader:
            catalog = line[catalog_idx]
            dataset_id = line[dataset_id_idx]
            if catalog not in self.catalogs:  # Inicializo
                self.catalogs[catalog] = []

            self.catalogs[catalog].append(dataset_id)

    def update_database(self):
        for catalog, datasets in self.catalogs.items():
            dataset_models = Catalog.objects.get_or_create(identifier=catalog)[0].dataset_set
            for dataset in datasets:
                status = 'OK'
                try:
                    dataset_model = dataset_models.get(identifier=dataset)
                    dataset_model.indexable = True
                    dataset_model.save()
                except Dataset.DoesNotExist:
                    status = 'ERROR'

                self.logs.append(DATASET_STATUS.format(catalog, dataset, status))


def process_node_register_file(register_file):
    """Registra (crea objetos Node) los nodos marcados como federado en el registro"""
    indexing_file = register_file.indexing_file
    yml = indexing_file.read()
    nodes = yaml.load(yml)
    for node, values in nodes.items():
        if bool(values['federado']) is True:  # evitar entrar al branch con un valor truthy
            try:
                node = Node.objects.get(catalog_id=node)
            except Node.DoesNotExist:
                node = Node(catalog_id=node)

            node.catalog_url = values['url']
            node.indexable = True
            node.save()

    register_file.state = NodeRegisterFile.PROCESSED
    register_file.save()


def confirm_delete(node, register_files):
    """Itera sobre todos los registros y solo borra el nodo si no está registrado
    como federado en ninguno de ellos"""
    found = False
    for register_file in register_files:
        indexing_file = register_file.indexing_file
        yml = indexing_file.read()
        nodes = yaml.load(yml)
        if node.catalog_id in nodes and nodes[node.catalog_id].get('federado'):
            found = True
            break

    if not found:
        node.delete()
