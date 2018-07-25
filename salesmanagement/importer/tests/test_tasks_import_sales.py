from datetime import date
from unittest.mock import patch
from django.test import TestCase

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.importer.tasks import import_sales_task
from salesmanagement.manager.models import Product, ProductCategory, ProductsSale, Company


class ImportSalesTaskTest(TestCase):
    @patch.object(SalesImportFile.objects, 'get')
    def setUp(self, mock_get):
        data = [
            {'product': 'Product Low', 'category': 'Category A', 'sold': 9, 'cost': 4.70, 'total': 47.30},
            {'product': 'Product High', 'category': 'Category B', 'sold': 5, 'cost': 3.20, 'total': 107.50}
        ]
        self.company = Company.objects.create(name='Company Name')
        mock_get.return_value.company = self.company
        mock_get.return_value.month = date.today().replace(day=1)
        with patch.object(ParserSalesXlsx, 'as_data', return_value=data):
            import_sales_task(1)

    def test_must_create_product_categories(self):
        """Must create 2 product categories"""
        self.assertEqual(2, ProductCategory.objects.count())

    def test_must_create_products(self):
        """Must create 2 products"""
        self.assertEqual(2, Product.objects.count())

    def test_products_must_have_company(self):
        """Must add company to products"""
        product = Product.objects.first()
        companies = product.company.all()
        self.assertIn(self.company, companies)

    def test_must_create_products_sale(self):
        """Must create 2 products sales"""
        self.assertEqual(2, ProductsSale.objects.count())
