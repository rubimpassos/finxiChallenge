from django.shortcuts import resolve_url as r
from django.test import TestCase

from salesmanagement.core.factories import RandomUserFactory


class HomeAnonymousUserTest(TestCase):
    def setUp(self):
        self.response = self.client.get(r('home'))

    def test_get(self):
        """GET / must return status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use index.html"""
        self.assertTemplateUsed(self.response, 'index.html')

    def test_login_link(self):
        expected = 'href="{}"'.format(r('login'))
        self.assertContains(self.response, expected)

    def test_not_have_logout_link(self):
        unexpected = 'href="{}"'.format(r('logout'))
        self.assertNotContains(self.response, unexpected)

    def test_sales_import_link(self):
        expected = 'href="{}"'.format(r('importer:sales-import'))
        self.assertContains(self.response, expected)


class HomeLoggedUserTest(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        self.client.login(username=user.username, password='pass')
        self.response = self.client.get(r('home'))

    def test_get(self):
        """GET / must return status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use index.html"""
        self.assertTemplateUsed(self.response, 'index.html')

    def test_logout_link(self):
        expected = 'href="{}"'.format(r('logout'))
        self.assertContains(self.response, expected)

    def test_not_have_login_link(self):
        unexpected = 'href="{}"'.format(r('login'))
        self.assertNotContains(self.response, unexpected)

    def test_sales_import_link(self):
        expected = 'href="{}"'.format(r('importer:sales-import'))
        self.assertContains(self.response, expected)
