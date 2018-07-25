from datetime import datetime

from django.test import TestCase

from salesmanagement.manager.models import Company, Product, ProductCategory


class ProductModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProductModelTest, cls).setUpClass()
        company = Company.objects.create(name='Company name')
        category = ProductCategory.objects.create(name='Category A')
        cls.obj = Product.objects.create(name='Product name', category=category)
        cls.obj.company.set([company])

    def test_create(self):
        self.assertTrue(Product.objects.exists())

    def test_category(self):
        """Must have category foreign field"""
        self.assertTrue(self.obj.category, ProductCategory)

    def test_company(self):
        """Must have company many-to-many field"""
        self.assertEqual('ManyRelatedManager', type(self.obj.company).__name__)
        self.assertEqual(self.obj.company.model, Company)
        self.assertTrue(self.obj.company.exists())

    def test_created(self):
        """Product must have an self-managed created datetime field"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified(self):
        """Product must have an self-managed modified datetime field"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual('Product name', str(self.obj))
