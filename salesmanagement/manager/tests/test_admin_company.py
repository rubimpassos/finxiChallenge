import re
from datetime import date

from django.contrib import admin
from django.test import TestCase
from djmoney.money import Money

from salesmanagement.manager.admin import CompanyAdmin
from salesmanagement.manager.factories import CompanyFactory, ProductFactory, ProductsSaleFactory
from salesmanagement.manager.models import Company


class CompanyAdminTest(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.admin = CompanyAdmin(Company, admin.site)

    def test_products_count_field(self):
        """products_count must be installed"""
        self.assertIn('products_count', self.admin.fields)
        self.assertIn('products_count', self.admin.readonly_fields)

    def test_products_count_result(self):
        """Must return all products count from company"""
        self.add_products()
        self.assertEqual(3, self.admin.products_count(self.company))

    def test_products_count_result_when_no_products(self):
        """Must return 0 products count because they don't exist"""
        self.assertEqual(0, self.admin.products_count(self.company))

    def test_sold_products_field(self):
        """sold_products must be installed"""
        self.assertIn('sold_products', self.admin.fields)
        self.assertIn('sold_products', self.admin.readonly_fields)

    def test_sold_products_result(self):
        """Must return sold products count from company"""
        self.add_products_and_sales()
        self.assertEqual(29, self.admin.sold_products(self.company))

    def test_sold_products_result_when_no_sales(self):
        """Must return 0 for sold products because they don't exists"""
        self.assertEqual(0, self.admin.sold_products(self.company))

    def test_best_seller_field(self):
        """best_seller must be installed"""
        self.assertIn('best_seller', self.admin.fields)
        self.assertIn('best_seller', self.admin.readonly_fields)

    def test_best_seller_result(self):
        """Must return best seller product url from company
        the priority is decided by the product that was first best seller, in case of tie
        """
        self.add_products_and_sales()
        link = self.admin.best_seller(self.company)
        self.assertIn('<a href=', link)
        self.assertIn('change', link)
        self.assertIn(f'?_changelist_filters=company__id__exact%3D{self.company.pk}', link)
        self.assertIn(str(self.products[0]), link)

    def test_related_links_field(self):
        """related_links must be installed"""
        self.assertIn('related_links', self.admin.fields)
        self.assertIn('related_links', self.admin.readonly_fields)

    def test_related_links_result(self):
        """Must return links to list filter, all filtered by company"""
        links = self.admin.related_links(self.company)
        matchs = self.match_related_links(links)
        self.assertTrue(matchs)
        self.assertIn('<a class="list_filter_link" href=', links)

    def test_related_links_media(self):
        """Must add a related_links.css"""
        self.assertIn('css/related_links.css', self.admin.Media.css['all'])

    def test_related_link_produtcs_field(self):
        """related_link_products must be installed"""
        self.assertIn('related_link_products', self.admin.fields_related_links)

    def test_related_link_produtcs_result(self):
        """Must return link to produtc list filter, filtered by company"""
        links = self.admin.related_link_products(self.company)
        matchs = self.match_related_links(links)
        self.assertTrue(matchs)
        self.assertIn('product', matchs[0])

    def test_related_link_sales_field(self):
        """related_link_sales must be installed"""
        self.assertIn('related_link_sales', self.admin.fields_related_links)

    def test_related_link_sales_result(self):
        """Must return link to sales list filter, filtered by company"""
        links = self.admin.related_link_sales(self.company)
        matchs = self.match_related_links(links)
        self.assertTrue(matchs)
        self.assertIn('productssale', matchs[0])

    def add_products(self):
        self.products = ProductFactory.create_batch(3, companies=(self.company,))

    def add_products_and_sales(self):
        self.add_products()
        month_june = date(day=1, month=6, year=2018)
        month_july = date(day=1, month=7, year=2018)
        sales_data = (dict(product=self.products[0], sold=5, cost=Money(3.5, 'BRL'), total=Money(57.5, 'BRL'),
                           sale_month=month_june),
                      dict(product=self.products[0], sold=7, cost=Money(3.5, 'BRL'), total=Money(35.3, 'BRL'),
                           sale_month=month_july),
                      dict(product=self.products[1], sold=2, cost=Money(10, 'BRL'), total=Money(27.5, 'BRL'),
                           sale_month=month_june),
                      dict(product=self.products[1], sold=10, cost=Money(10, 'BRL'), total=Money(200, 'BRL'),
                           sale_month=month_july),
                      dict(product=self.products[2], sold=4, cost=Money(1.99, 'BRL'), total=Money(39.8, 'BRL'),
                           sale_month=month_june),
                      dict(product=self.products[2], sold=1, cost=Money(1.99, 'BRL'), total=Money(6.3, 'BRL'),
                           sale_month=month_july),)
        self.sales = []
        for params in sales_data:
            self.sales.append(ProductsSaleFactory(company=self.company, **params))

    def match_related_links(self, links):
        regex = fr'<a class="list_filter_link" href="(.*)\?company__id__exact={self.company.pk}' \
                fr'&_disable_filters=company'
        return re.findall(regex, links)
