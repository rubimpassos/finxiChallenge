from datetime import datetime

from django.test import TestCase

from salesmanagement.manager.models import ProductCategory


class ProductCategoryModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProductCategoryModelTest, cls).setUpClass()
        cls.obj = ProductCategory.objects.create(name='Category name')

    def test_create(self):
        self.assertTrue(ProductCategory.objects.exists())

    def test_created(self):
        """Company must have an self-managed created datetime field"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified(self):
        """Company must have an self-managed modified datetime field"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual('Category name', str(self.obj))
