from unittest.mock import MagicMock, patch

from django.db.models.signals import post_save
from django.test import TestCase

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.receivers import post_save_sales_import_file


class SalesImportFileModelPostSaveReceiverTest(TestCase):
    def test_receiver_registered(self):
        """Should register post_save_sales_import_file in pos_save with SalesImportFile sender"""
        receivers = post_save._live_receivers(SalesImportFile)
        receiver_strings = ["{}.{}".format(r.__module__, r.__name__) for r in receivers]
        self.assertIn('salesmanagement.importer.receivers.post_save_sales_import_file', receiver_strings)

    def test_receiver_has_dispatch_uid(self):
        """Should have import_sales_handler dispatch_uid"""
        lookup_keys = [r[0][0] for r in post_save.receivers]
        self.assertIn('post_save_sales_import_file', lookup_keys)

    @patch('salesmanagement.importer.tasks.import_sales_task.delay')
    def test_import_sales_task_called_once(self, mock_import):
        """Must call import_sale_task to celery"""
        instance = MagicMock()
        instance.pk = 1
        post_save_sales_import_file(SalesImportFile, instance)

        mock_import.assert_called_once_with(1)
