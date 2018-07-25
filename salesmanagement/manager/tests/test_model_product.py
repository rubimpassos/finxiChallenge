from datetime import datetime

from django.test import TestCase

from salesmanagement.manager.models import Company, Product, ProductCategory


class ProductModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProductModelTest, cls).setUpClass()
        category = ProductCategory.objects.create(name='Category A')
        cls.obj = Product.objects.create(name='Product name', category=category)

    def test_create(self):
        self.assertTrue(Product.objects.exists())

    def test_category(self):
        """Must have category attr"""
        self.assertTrue(self.obj.category, ProductCategory)

    def test_created(self):
        """Product must have an self-managed created attr"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified(self):
        """Product must have an self-managed modified attr"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual('Product name', str(self.obj))
