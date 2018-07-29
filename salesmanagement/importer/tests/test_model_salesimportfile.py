from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from salesmanagement.importer.factories import SalesImportFileFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tests import mock_storage


class SalesImportFileModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with mock_storage('sales_imported_files/FileName_0.xlsx'):
            cls.obj = SalesImportFileFactory.create()

    def test_create(self):
        self.assertTrue(SalesImportFile.objects.exists())

    def test_user_field(self):
        self.assertIsInstance(self.obj.user, get_user_model())

    def test_company_field(self):
        self.assertEqual('Company Name 0', self.obj.company.name)

    def test_month_field(self):
        self.assertIsInstance(self.obj.month, date)

    def test_file_field(self):
        self.assertEqual('sales_imported_files/FileName_0.xlsx', self.obj.file.name)

    def test_created_field(self):
        """SalesImportFile must have an self-managed created attr"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified_field(self):
        """SalesImportFile must have an self-managed modified attr"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual("Registro de vendas de Company Name 0 no mês de Julho de 2018", str(self.obj))
