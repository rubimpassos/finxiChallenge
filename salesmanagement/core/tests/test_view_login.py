from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import resolve_url as r
from django.test import TestCase

from salesmanagement.core.factories import RandomUserFactory


class LoginViewGet(TestCase):
    def setUp(self):
        self.response = self.client.get(r('login'))

    def test_get(self):
        """GET / must return status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use login.html"""
        self.assertTemplateUsed(self.response, 'login.html')

    def test_html(self):
        """Html must contain specific form and input tags"""
        tags = (('<form novalidate method="post">', 1),
                ('<input', 4),
                ('type="text"', 1),
                ('type="password"', 1),
                ('type="submit"', 1))

        for text, count in tags:
            with self.subTest():
                self.assertContains(self.response, text, count)

    def test_csrf(self):
        """Html must contain csrf"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_has_form(self):
        """Context must have authenticate form"""
        form = self.response.context['form']
        self.assertTrue(form, AuthenticationForm)


class LoginViewPostValid(TestCase):
    def setUp(self):
        RandomUserFactory(username='user', password='pass')
        self.data = dict(username='user', password='pass')

    def test_post_default_redirect(self):
        """Must redirect to home"""
        response = self.client.post(r('login'), self.data)
        self.assertRedirects(response, r('home'))

    def test_post_next_redirect(self):
        """Must redirect to next page"""
        expected = '/next-page-redirect/'
        self.data['next'] = expected
        response = self.client.post(r('login'), self.data)
        self.assertRedirects(response, expected, target_status_code=404)


class LoginViewPostInvalid(TestCase):
    def setUp(self):
        self.response = self.client.post(r('login'), {})

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use login.html"""
        self.assertTemplateUsed(self.response, 'login.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, AuthenticationForm)
