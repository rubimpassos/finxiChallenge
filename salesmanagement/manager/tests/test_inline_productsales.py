from datetime import date
from unittest.mock import MagicMock

from django.contrib import admin
from django.test import TestCase
from djmoney.money import Money

from salesmanagement.manager.factories import ProductFactory, CompanyFactory, ProductsSaleFactory
from salesmanagement.manager.inlines import ProductSalesInline
from salesmanagement.manager.models import ProductsSale


class ProductSalesInlineTest(TestCase):
    def setUp(self):
        self.companies = CompanyFactory.create_batch(2)
        self.product = ProductFactory.create(companies=self.companies)
        month_july = date(day=1, month=7, year=2018)
        sales_data = (dict(company=self.companies[0], product=self.product, sold=7, cost=Money(3.5, 'BRL'),
                           total=Money(35, 'BRL'), sale_month=month_july),
                      dict(company=self.companies[1], product=self.product, sold=7, cost=Money(4.5, 'BRL'),
                           total=Money(105, 'BRL'), sale_month=month_july),)
        self.sales = []
        for params in sales_data:
            self.sales.append(ProductsSaleFactory(**params))

        self.admin = ProductSalesInline(ProductsSale, admin.site)

    def test_price_field(self):
        """price must be installed"""
        self.assertIn('price', self.admin.fields)
        self.assertIn('price', self.admin.readonly_fields)

    def test_price_result(self):
        """Must return price from product"""
        self.assertEqual(Money(5, 'BRL'), self.admin.price(self.sales[0]))

    def test_month_year_field(self):
        """month_year must be installed"""
        self.assertIn('month_year', self.admin.fields)
        self.assertIn('month_year', self.admin.readonly_fields)

    def test_month_year_result(self):
        """Must return month_year from product"""
        self.assertEqual('Julho de 2018', self.admin.month_year(self.sales[0]))

    def test_queryset_filtered_by_company(self):
        """Must return only sales from company"""
        self.admin.request = MagicMock(GET={'company__id__exact': self.companies[0].pk})
        expected = ProductsSale.objects.filter(company=self.companies[0])
        self.assertQuerysetEqual(self.admin.get_queryset(self.admin.request), expected, transform=lambda x: x)
