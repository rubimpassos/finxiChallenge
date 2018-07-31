from datetime import date
from unittest.mock import MagicMock

from django.contrib import admin
from django.test import TestCase
from djmoney.money import Money

from salesmanagement.manager.admin import ProductsSaleAdmin
from salesmanagement.manager.factories import ProductFactory, CompanyFactory, ProductsSaleFactory
from salesmanagement.manager.models import ProductsSale


class ProductsSalesAdminTest(TestCase):
    def setUp(self):
        self.companies = CompanyFactory.create_batch(2)
        self.product = ProductFactory.create(companies=self.companies, category__name='Category Name')
        month_july = date(day=1, month=7, year=2018)
        sales_data = (dict(company=self.companies[0], product=self.product, sold=7, cost=Money(3.5, 'BRL'),
                           total=Money(35, 'BRL'), sale_month=month_july),
                      dict(company=self.companies[1], product=self.product, sold=7, cost=Money(4.5, 'BRL'),
                           total=Money(105, 'BRL'), sale_month=month_july),)
        self.sales = []
        for params in sales_data:
            self.sales.append(ProductsSaleFactory(**params))

        self.admin = ProductsSaleAdmin(ProductsSale, admin.site)

    def test_media_assets(self):
        """Must add a related_links.css"""
        self.assertIn('js/list_filter_collapse.js', self.admin.Media.js)

    def test_category_field(self):
        """category must be installed"""
        self.assertIn('category', self.admin.list_display)
        self.assertIn('category', self.admin.readonly_fields)

    def test_category_result(self):
        """Must return category from product"""
        self.assertEqual('Category Name', self.admin.category(self.sales[0]))

    def test_month_year_field(self):
        """month_year must be installed"""
        self.assertIn('month_year', self.admin.list_display)
        self.assertIn('month_year', self.admin.readonly_fields)

    def test_month_year_result(self):
        """Must return month year in full"""
        self.assertEqual('Julho de 2018', self.admin.month_year(self.sales[0]))

    def test_price_field(self):
        """month_year must be installed"""
        self.assertIn('price', self.admin.list_display)
        self.assertIn('price', self.admin.readonly_fields)

    def test_price_result(self):
        """Must return sale estimated price"""
        self.assertEqual(Money(5, 'BRL'), self.admin.price(self.sales[0]))

    def test_queryset_filtered_by_company(self):
        """Must return only sales from company filter"""
        self.admin.request = MagicMock(GET={'company__id__exact': self.companies[0].pk})
        expected = ProductsSale.objects.filter(company=self.companies[0])
        self.assertQuerysetEqual(self.admin.get_queryset(self.admin.request), expected, transform=lambda x: x)

    def test_disable_filters(self):
        """Must remove filter that's in _disable_filters from list_filter"""
        self.admin.request = MagicMock(GET={'_disable_filters': 'company'})
        self.admin.list_filter = ('company', 'product', 'cost')
        list_filter = self.admin.get_list_filter(self.admin.request)
        self.assertEqual(['product', 'cost'], list_filter)
