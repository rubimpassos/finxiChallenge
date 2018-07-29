from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test import TestCase
from notifications.models import Notification

from salesmanagement.core.factories import RandomUserFactory


class NotificationInAnyViewLoggedUserTest(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        Notification.objects.create(actor=user, recipient=user)
        self.client.login(username=user.username, password='pass')
        self.response = self.client.get('/')

    def test_contain_js(self):
        self.assertContains(self.response, static('js/notifications.js'))

    def test_html(self):
        """Html must contain specific input tags"""
        tags = (('<ul id="notifications">', 1),
                ('<button data-remove-url="', 1))

        for text, count in tags:
            with self.subTest():
                self.assertContains(self.response, text, count)


class NotificationAnyViewAnonymousUserTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/')

    def test_not_contain_js(self):
        response = self.client.get('/')
        self.assertNotContains(response, static('js/notifications.js'))

    def test_html(self):
        """Html must not contain specific input tags"""
        tags = ('<ul id="notifications">', '<button data-remove-url="')

        for text in tags:
            with self.subTest():
                self.assertNotContains(self.response, text)
