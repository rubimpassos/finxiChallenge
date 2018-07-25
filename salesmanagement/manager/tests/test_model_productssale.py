from datetime import datetime, date

from django.test import TestCase
from djmoney.money import Money

from salesmanagement.manager.models import Company, ProductsSale, Product, ProductCategory


class ProductsSaleModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProductsSaleModelTest, cls).setUpClass()
        company = Company.objects.create(name='Company name')
        category = ProductCategory.objects.create(name='Category name')
        product = Product.objects.create(name='Product name', category=category)
        product.company.add(company)
        sale_month = date(day=1, month=7, year=2018)
        cls.obj = ProductsSale.objects.create(
            company=company,
            product=product,
            sold=10,
            cost=5.6,
            total=150.5,
            sale_month=sale_month,
        )

    def test_create(self):
        self.assertTrue(ProductsSale.objects.exists())

    def test_company(self):
        """Must have company foreign field"""
        self.assertIsInstance(self.obj.company, Company)

    def test_product(self):
        """Must have product foreign field"""
        self.assertIsInstance(self.obj.product, Product)

    def test_sold(self):
        """Must have sold int field"""
        self.assertIsInstance(self.obj.sold, int)

    def test_cost(self):
        """Must have cost money field"""
        self.assertEqual(Money(5.6, 'BRL'), self.obj.cost)

    def test_total(self):
        """Must have total money field"""
        self.assertEqual(Money(150.5, 'BRL'), self.obj.total)

    def test_sale_month(self):
        """Must have sale_month field"""
        self.assertIsInstance(self.obj.sale_month, date)

    def test_price(self):
        """Must have sale price method as money field"""
        sold = 10
        total = 150.5
        expected = Money(total/sold, 'BRL')
        self.assertEqual(expected, self.obj.price)

    def test_created(self):
        """Company must have an self-managed created datetime field"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified(self):
        """Company must have an self-managed modified datetime field"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual('[Company name]Vendas de Product name em Julho de 2018', str(self.obj))
