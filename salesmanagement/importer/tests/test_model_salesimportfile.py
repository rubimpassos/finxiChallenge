from datetime import date, datetime
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.test import TestCase

from salesmanagement.importer.factories import SalesImportFileFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tests import mock_storage


class SalesImportFileModelTest(TestCase):
    def setUp(self):
        self.task_patcher = patch('salesmanagement.importer.tasks.import_sales_task.delay')
        self.storage_patcher = mock_storage('sales_imported_files/FileName.xlsx')
        self.notify_patcher = patch("salesmanagement.importer.models.notify", return_value=MagicMock(send=MagicMock()))
        with self.task_patcher as task_mock, self.storage_patcher, self.notify_patcher as notify_mock:
            self.notify_mock = notify_mock
            self.task_mock = task_mock
            self.obj = SalesImportFileFactory.create(company__name='Company Name')

    def test_create(self):
        self.assertTrue(SalesImportFile.objects.exists())

    def test_user_field(self):
        self.assertIsInstance(self.obj.user, get_user_model())

    def test_company_field(self):
        self.assertEqual('Company Name', self.obj.company.name)

    def test_month_field(self):
        self.assertIsInstance(self.obj.month, date)

    def test_file_field(self):
        self.assertEqual('sales_imported_files/FileName.xlsx', self.obj.file.name)

    def test_status_field(self):
        self.assertEqual('PROCESSING', self.obj.status)

    def test_status_choices(self):
        self.assertEqual('PROCESSING', SalesImportFile.PROCESSING)
        self.assertEqual('IMPORTED', SalesImportFile.IMPORTED)
        self.assertEqual('ERROR', SalesImportFile.ERROR)

    def test_status_choices_str(self):
        self.assertEqual('Em processamento', SalesImportFile.STATUS[0][1])
        self.assertEqual('Importado com sucesso', SalesImportFile.STATUS[1][1])
        self.assertEqual('Falha ao importar os dados, verifique o arquivo e envie-o novamente!',
                         SalesImportFile.STATUS[2][1])

    def test_default_satatus(self):
        """Must starts with PROCESSING status"""
        self.assertEqual('PROCESSING', self.obj.status)

    def test_imported(self):
        """Must set IMPORTED status"""
        self.obj.imported()
        self.assertEqual('IMPORTED', self.obj.status)

    def test_imported_fail(self):
        """Must set ERROR status and send notifcation"""
        self.obj.imported_fail()
        self.assertEqual('ERROR', self.obj.status)

    def test_created_field(self):
        """SalesImportFile must have an self-managed created attr"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified_field(self):
        """SalesImportFile must have an self-managed modified attr"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual("Registro de vendas de Company Name do mês de Julho de 2018", str(self.obj))

    def test_call_importer_on_create_file(self):
        """Must call task to import data file on create"""
        self.task_mock.assert_called_once_with(self.obj.pk)

    def test_call_importer_on_change_file(self):
        """Must call task to import data file on change"""
        with self.task_patcher as task_mock, self.storage_patcher:
            self.obj.file = 'FileNameDiff.xlsx'
            self.obj.save()
            task_mock.assert_called_once_with(self.obj.pk)

    def test_not_call_importer_on_changed_but_not_file_field(self):
        """Must not call task import on change when file field won't was changed"""
        with self.task_patcher as task_mock, self.storage_patcher:
            self.obj.file = 'sales_imported_files/FileName.xlsx'
            self.obj.save()
            task_mock.assert_not_called()

    def test_notify_on_status_imported(self):
        """Must send notification when status changed to IMPORTED"""
        with self.notify_patcher as mock:
            self.obj.status = 'IMPORTED'
            self.obj.save()
            mock.send.assert_called_once_with(self.obj, recipient=self.obj.user, verb=_('foi importado'))

    def test_notify_on_status_error(self):
        """Must send notification when status changed to error"""
        with self.notify_patcher as mock:
            self.obj.status = 'ERROR'
            self.obj.save()
            mock.send.assert_called_once_with(self.obj, recipient=self.obj.user, verb=_('falhou ao ser importado'))

    def test_not_notify_on_status_invalid(self):
        """Must not send notifications when status changed to something different from IMPORTED or ERROR"""
        with self.notify_patcher as mock:
            self.obj.status = 'TESTE'
            self.obj.save()
            mock.send.assert_not_called()

