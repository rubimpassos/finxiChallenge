from datetime import date
from unittest.mock import MagicMock

from django.contrib import admin
from django.test import TestCase
from djmoney.money import Money

from salesmanagement.manager.admin import ProductAdmin
from salesmanagement.manager.factories import CompanyFactory, ProductFactory, ProductsSaleFactory
from salesmanagement.manager.inlines import ProductSalesInline
from salesmanagement.manager.models import Product


class ProductAdminTest(TestCase):
    def setUp(self):
        self.companies = CompanyFactory.create_batch(2)
        self.product = ProductFactory.create(companies=self.companies)
        self.admin = ProductAdmin(Product, admin.site)

    def test_productssales_inlines(self):
        """ProducSalesInline must be installed"""
        self.assertIn(ProductSalesInline, self.admin.inlines)

    def test_media_assets(self):
        """Must add a related_links.css"""
        self.assertIn('js/list_filter_collapse.js', self.admin.Media.js)

    def test_current_cost_field(self):
        """current_cost must be installed"""
        self.assertIn('current_cost', self.admin.list_display)
        self.assertIn('current_cost', self.admin.fields)
        self.assertIn('current_cost', self.admin.readonly_fields)

    def test_current_cost_result(self):
        """Must return current product cost"""
        self.add_products_and_sales()
        self.admin.request = MagicMock(GET={})
        self.assertEqual(Money(4.5, 'BRL'), self.admin.current_cost(self.product))

    def test_current_cost_result_filtered_by_company_changelist(self):
        """Must return current product cost filtered by company in change list view"""
        self.add_products_and_sales()
        self.admin.request = MagicMock(GET={'company__id__exact': self.companies[0].pk})
        self.assertEqual(Money(3.5, 'BRL'), self.admin.current_cost(self.product))

    def test_current_cost_result_filtered_by_company_change_view(self):
        """Must return current product cost filtered by company in change view"""
        self.add_products_and_sales()
        get_data = dict(_changelist_filters=f'company__id__exact={self.companies[0].pk}')
        self.admin.request = MagicMock(GET=get_data)
        self.assertEqual(Money(3.5, 'BRL'), self.admin.current_cost(self.product))

    def test_current_price_field(self):
        """current_price must be installed"""
        self.assertIn('current_price', self.admin.list_display)
        self.assertIn('current_price', self.admin.fields)
        self.assertIn('current_price', self.admin.readonly_fields)

    def test_current_price_result(self):
        """Must return current product price"""
        self.add_products_and_sales()
        self.admin.request = MagicMock(GET={})
        self.assertEqual(Money(15, 'BRL'), self.admin.current_price(self.product))

    def test_current_price_result_filtered_by_company_changelist(self):
        """Must return current product price filtered by company in change list view"""
        self.add_products_and_sales()
        self.admin.request = MagicMock(GET={'company__id__exact': self.companies[0].pk})
        self.assertEqual(Money(5, 'BRL'), self.admin.current_price(self.product))

    def test_current_price_result_filtered_by_company_change_view(self):
        """Must return current product price filtered by company in change view"""
        self.add_products_and_sales()
        get_data = dict(_changelist_filters=f'company__id__exact={self.companies[0].pk}')
        self.admin.request = MagicMock(GET=get_data)
        self.assertEqual(Money(5, 'BRL'), self.admin.current_price(self.product))

    def test_queryset_filtered_by_company(self):
        """Must return only products from company filter"""
        # create one product that only self.companies[0] has
        ProductFactory.create(companies=(self.companies[0],))

        # filter by self.companies[1]
        self.admin.request = MagicMock(GET={'company__id__exact': self.companies[1].pk})
        expected = Product.objects.filter(company=self.companies[1])

        self.assertQuerysetEqual(self.admin.get_queryset(self.admin.request), expected, transform=lambda x: x)

    def test_disable_filters(self):
        """Must remove filter that's in _disable_filters from list_filter"""
        self.admin.request = MagicMock(GET={'_disable_filters': 'company'})
        self.admin.list_filter = ('name', 'category', 'company')
        list_filter = self.admin.get_list_filter(self.admin.request)
        self.assertEqual(['name', 'category'], list_filter)

    def add_products_and_sales(self):
        month_june = date(day=1, month=7, year=2018)
        month_july = date(day=1, month=7, year=2018)
        sales_data = (dict(company=self.companies[0], product=self.product, sold=5, cost=Money(3.5, 'BRL'),
                           total=Money(57.5, 'BRL'), sale_month=month_june),
                      dict(company=self.companies[0], product=self.product, sold=7, cost=Money(3.5, 'BRL'),
                           total=Money(35, 'BRL'), sale_month=month_july),
                      dict(company=self.companies[1], product=self.product, sold=7, cost=Money(4.5, 'BRL'),
                           total=Money(55.5, 'BRL'), sale_month=month_june),
                      dict(company=self.companies[1], product=self.product, sold=7, cost=Money(4.5, 'BRL'),
                           total=Money(105, 'BRL'), sale_month=month_july),)
        self.sales = []
        for params in sales_data:
            self.sales.append(ProductsSaleFactory(**params))
