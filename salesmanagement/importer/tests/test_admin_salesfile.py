from unittest.mock import patch, MagicMock

from django.contrib import admin
from django.test import TestCase

from salesmanagement.importer.admin import SalesFileAdmin
from salesmanagement.importer.factories import SalesImportFileFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tests import mock_storage


class SalesFileAdminTest(TestCase):
    def setUp(self):
        self.task_patcher = patch('salesmanagement.importer.tasks.import_sales_task.delay')
        self.storage_patcher = mock_storage('sales_imported_files/FileName.xlsx')
        self.notify_patcher = patch("salesmanagement.importer.models.notify", return_value=MagicMock(send=MagicMock()))
        with self.task_patcher as task_mock, self.storage_patcher, self.notify_patcher as notify_mock:
            self.notify_mock = notify_mock
            self.task_mock = task_mock
            self.obj = SalesImportFileFactory.create(company__name='Company Name', status=SalesImportFile.IMPORTED)

        self.admin = SalesFileAdmin(SalesImportFile, admin.site)

    def test_filename_field(self):
        """filename must be installed"""
        self.assertIn('filename', self.admin.list_display)
        self.assertIn('filename', self.admin.readonly_fields)

    def test_filename_result(self):
        """Must return month year in full"""
        self.assertEqual('FileName.xlsx', self.admin.filename(self.obj))

    def test_month_year_field(self):
        """month_year must be installed"""
        self.assertIn('month_year', self.admin.list_display)
        self.assertIn('month_year', self.admin.readonly_fields)

    def test_month_year_result(self):
        """Must return month year in full"""
        self.assertEqual('Julho de 2018', self.admin.month_year(self.obj))

    def test_imported_field(self):
        """imported must be installed"""
        self.assertIn('imported', self.admin.list_display)
        self.assertIn('imported', self.admin.readonly_fields)

    def test_imported_result(self):
        """Must return if status is IMPORTED"""
        self.assertTrue(self.admin.imported(self.obj))
