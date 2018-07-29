from django.shortcuts import resolve_url as r
from django.test import TestCase

from salesmanagement.core.factories import RandomUserFactory


class LogoutViewGet(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        self.client.login(username=user.username, password='pass')
        self.response = self.client.get(r('logout'))

    def test_get(self):
        """Must redirect to home"""
        self.assertRedirects(self.response, r('home'))
