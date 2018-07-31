from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase
from djmoney.money import Money
from django.utils.translation import gettext as _

from salesmanagement.importer.factories import SalesImportFileFactory
from salesmanagement.importer.tests import mock_storage
from salesmanagement.manager.factories import CompanyFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.importer.tasks import import_sales_task
from salesmanagement.manager.models import Product, ProductCategory, ProductsSale


class ImportSalesTaskSuccessTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        parsed_xlsx = [
            {'product': 'Product Low', 'category': 'Category A', 'sold': 9, 'cost': Money(4.7, 'BRL'),
             'total': Money(47.3, 'BRL')},
            {'product': 'Product Low', 'category': 'Category A', 'sold': 7, 'cost': Money(5.70, 'BRL'),
             'total': Money(90.30, 'BRL')},
            {'product': 'Product High', 'category': 'Category B', 'sold': 5, 'cost': Money(3.2, 'BRL'),
             'total': Money(107.5, 'BRL')}
        ]

        patcher_parser = patch.object(ParserSalesXlsx, 'as_data', return_value=parsed_xlsx)
        patcher_storage = mock_storage('sales_imported_files/FileName.xlsx')
        notify_patcher = patch("salesmanagement.importer.models.notify", return_value=MagicMock(send=MagicMock()))

        with patcher_storage, patcher_parser, notify_patcher:
            cls.sale_file = SalesImportFileFactory.create(company__name='Company Name')
            import_sales_task(cls.sale_file.pk)

    def test_status_imported(self):
        """Must set status field to IMPORTED"""
        self.sale_file = SalesImportFile.objects.get(pk=self.sale_file.pk)
        self.assertEqual(SalesImportFile.IMPORTED, self.sale_file.status)

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

    def test_products_sale_sold_count(self):
        """Must sum sold count if have repeated products"""
        products = [('Product Low', 16), ('Product High', 5)]
        sales = [(sale.product.name, sale.sold) for sale in ProductsSale.objects.all()]
        self.assertEqual(products, sales)

    def test_products_sale_total_count(self):
        """Must sum total count if have repeated products"""
        products = [('Product Low', Money(137.60, 'BRL')), ('Product High', Money(107.5, 'BRL'))]
        sales = [(sale.product.name, sale.total) for sale in ProductsSale.objects.all()]
        self.assertEqual(products, sales)


class ImportSalesTaskFailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        patcher_parser = patch.object(ParserSalesXlsx, 'as_data', return_value=[])
        patcher_storage = mock_storage('sales_imported_files/FileName.xlsx')
        notify_patcher = patch("salesmanagement.importer.models.notify", return_value=MagicMock(send=MagicMock()))

        with patcher_storage, patcher_parser, notify_patcher:
            cls.sale_file = SalesImportFileFactory.create(company__name='Company Name')
            import_sales_task(cls.sale_file.pk)

    def test_status_imported(self):
        """Must set status field to ERROR"""
        self.sale_file = SalesImportFile.objects.get(pk=self.sale_file.pk)
        self.assertEqual(SalesImportFile.ERROR, self.sale_file.status)
