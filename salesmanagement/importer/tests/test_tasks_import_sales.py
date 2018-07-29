from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase
from djmoney.money import Money
from django.utils.translation import gettext as _

from salesmanagement.importer.factories import CompanyFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.importer.tasks import import_sales_task
from salesmanagement.manager.models import Product, ProductCategory, ProductsSale


class ImportSalesTaskTest(TestCase):
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
        mock_attr = {
            'company': CompanyFactory.create(name='Company Name'),
            'month': date(day=1, month=7, year=2018),
            'file.path': 'FileName.xlsx'
        }
        patcher_get = patch.object(SalesImportFile.objects, 'get', return_value=MagicMock(**mock_attr))
        patcher_parser = patch.object(ParserSalesXlsx, 'as_data', return_value=parsed_xlsx)
        pathcer_notify = patch("salesmanagement.importer.tasks.notify", return_value=MagicMock(send=MagicMock()))

        with patcher_get as mock_sale, patcher_parser, pathcer_notify as mock_notify:
            cls.mock_sale = mock_sale()
            cls.mock_notify = mock_notify
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

    def test_send_notification(self):
        """Must send notification with args"""
        self.mock_notify.send.assert_called_once_with(self.mock_sale, recipient=self.mock_sale.user,
                                                      verb=_("foi importado"))
