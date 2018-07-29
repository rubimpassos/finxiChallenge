from django.test import TestCase
from notifications.models import Notification

from salesmanagement.core.factories import RandomUserFactory


class NotificationsContextLoggedUserTest(TestCase):
    def setUp(self):
        self.passord = 'pass'
        self.user = RandomUserFactory(password=self.passord)
        self.client.login(username=self.user.username, password='pass')

    def test_notification_context(self):
        Notification.objects.create(actor=self.user, recipient=self.user)
        response = self.client.get('/')
        self.assertIn('notifications', response.context)

    def test_notifications_not_exists(self):
        response = self.client.get('/')
        self.assertNotIn('notifications', response.context)


class NotificationsContextAnonymousUserTest(TestCase):
    def setUp(self):
        self.passord = 'pass'
        self.user = RandomUserFactory(password=self.passord)
        Notification.objects.create(actor=self.user, recipient=self.user)

    def test_notification_not_in_context(self):
        response = self.client.get('/')
        self.assertNotIn('notifications', response.context)
