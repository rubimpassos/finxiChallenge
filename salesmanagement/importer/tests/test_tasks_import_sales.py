from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase

from salesmanagement.importer.factories import CompanyFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.importer.tasks import import_sales_task
from salesmanagement.manager.models import Product, ProductCategory, ProductsSale, Company


class ImportSalesTaskTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        parsed_xlsx = [
            {'product': 'Product Low', 'category': 'Category A', 'sold': 9, 'cost': 4.70, 'total': 47.30},
            {'product': 'Product High', 'category': 'Category B', 'sold': 5, 'cost': 3.20, 'total': 107.50}
        ]
        mock_attr = {
            'company': CompanyFactory.create(name='Company Name'),
            'month': date(day=1, month=7, year=2018),
            'file.path': 'FileName.xlsx'
        }
        patcher_get = patch.object(SalesImportFile.objects, 'get', return_value=MagicMock(**mock_attr))
        patcher_parser = patch.object(ParserSalesXlsx, 'as_data', return_value=parsed_xlsx)

        with patcher_get, patcher_parser:
            import_sales_task(1)

    def test_must_create_product_categories(self):
        """Must create 2 product categories"""
        self.assertEqual(2, ProductCategory.objects.count())

    def test_must_create_products(self):
        """Must create 2 products"""
        self.assertEqual(2, Product.objects.count())

    def test_products_must_have_company(self):
        """Must have company in each product"""
        companies = Product.objects.all().values_list('company__name', flat=True)
        self.assertEqual(['Company Name', 'Company Name'], list(companies))

    def test_must_create_products_sale_with_values(self):
        """Must create 2 products sales with data values"""
        self.assertEqual(2, ProductsSale.objects.count())
