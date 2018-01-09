#! coding: utf-8
import os

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Node, NodeRegisterFile
from ..actions import process_node_register_file, confirm_delete

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class NodeRegisterFileTests(TestCase):

    def setUp(self):
        self.user = User(username='test_user', password='test_pass', email='test@email.com')
        self.user.save()

    def test_register_files_changes_state(self):
        filepath = os.path.join(dir_path, 'indice.yml')
        self.read_file(filepath)
        nrf = NodeRegisterFile.objects.first()
        self.assertEqual(nrf.state, NodeRegisterFile.PROCESSED)

    def test_register_file_creates_nodes(self):
        self.assertFalse(Node.objects.count())
        filepath = os.path.join(dir_path, 'indice.yml')
        self.read_file(filepath)

        self.assertTrue(Node.objects.count())

    def test_register_file_doesnt_create_non_federated_nodes(self):
        filepath = os.path.join(dir_path, 'indice.yml')
        self.read_file(filepath)
        non_federated = 'datosgobar'  # Marcado como 'federado: False' en el .yml
        self.assertFalse(Node.objects.filter(catalog_id=non_federated))

    def read_file(self, filepath):
        with open(filepath, 'r') as f:
            nrf = NodeRegisterFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                   uploader=self.user)
            nrf.save()
            process_node_register_file(register_file=nrf)

    def tearDown(self):
        self.user.delete()


class NodeTests(TestCase):

    def setUp(self):
        self.user = User(username='test_user', password='test_pass', email='test@email.com')
        self.user.save()

    def test_delete_federated_node_fails(self):
        filepath = os.path.join(dir_path, 'indice.yml')
        with open(filepath, 'r') as f:
            nrf = NodeRegisterFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                   uploader=self.user)
            nrf.save()
            process_node_register_file(register_file=nrf)

        register_files = NodeRegisterFile.objects.all()
        node = Node.objects.get(catalog_id='sspm')
        confirm_delete(node, register_files)

        # Esperado: el nodo no se borra porque está federado
        self.assertTrue(Node.objects.get(catalog_id='sspm'))

    def test_delete_non_federated_node(self):
        filepath = os.path.join(dir_path, 'indice.yml')
        with open(filepath, 'r') as f:
            nrf = NodeRegisterFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                   uploader=self.user)
            nrf.save()
            process_node_register_file(register_file=nrf)

        register_files = NodeRegisterFile.objects.all()
        register_files.delete()  # Fuerza a que los nodos no estén más federados
        node = Node.objects.get(catalog_id='sspm')
        confirm_delete(node, register_files)

        # Esperado: el nodo se borra porque no está federado
        self.assertFalse(Node.objects.filter(catalog_id='sspm'))

    def tearDown(self):
        self.user.delete()
