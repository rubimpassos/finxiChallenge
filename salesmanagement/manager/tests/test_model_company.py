from datetime import datetime

from django.test import TestCase

from salesmanagement.manager.models import Company


class CompanyModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CompanyModelTest, cls).setUpClass()
        cls.obj = Company.objects.create(name='Company name')

    def test_create(self):
        self.assertTrue(Company.objects.exists())

    def test_created(self):
        """Company must have an self-managed created datetime field"""
        self.assertIsInstance(self.obj.created, datetime)

    def test_modified(self):
        """Company must have an self-managed modified datetime field"""
        self.assertIsInstance(self.obj.modified, datetime)

    def test_str(self):
        self.assertEqual('Company name', str(self.obj))
