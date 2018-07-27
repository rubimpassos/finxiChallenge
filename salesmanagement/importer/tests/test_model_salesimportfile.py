from datetime import date, datetime

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tests import mock_storage, get_temporary_text_file, NoImportSalesSignalsTestCase
from salesmanagement.manager.models import Company


class SalesImportFileModelTest(NoImportSalesSignalsTestCase):
    def setUp(self):
        super(SalesImportFileModelTest, self).setUpClass()
        month = date.today().replace(day=1)

        self.company = Company.objects.create(name='Company Name')
        with mock_storage('sales_imported_files/FileName.xlsx'):
            self.obj = SalesImportFile.objects.create(company=self.company,
                                                      file=get_temporary_text_file("FileName.xlsx"),
                                                      month=month)

    def test_create(self):
        self.assertTrue(SalesImportFile.objects.exists())

    def test_month_field(self):
        """SalesImportFile must have an auto created attr"""
        self.assertIsInstance(self.obj.month, date)

    def test_created_field(self):
        """SalesImportFile must have an self-managed created attr"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified_field(self):
        """SalesImportFile must have an self-managed modified attr"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual("sales_imported_files/FileName.xlsx", str(self.obj))
