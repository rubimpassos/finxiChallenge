from datetime import date
from pathlib import Path

from django.contrib.messages import get_messages
from django.db.models import signals
from django.shortcuts import resolve_url as r
from django.test import TestCase
from factory.django import mute_signals

from salesmanagement.core.factories import RandomUserFactory
from salesmanagement.importer.factories import SalesImportFileFactory
from salesmanagement.manager.factories import CompanyFactory
from salesmanagement.importer.forms import SalesImportForm
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tests import get_temporary_text_file, mock_storage
from salesmanagement.manager.models import Company


class SalesImportViewGetValid(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        self.client.login(username=user.username, password='pass')
        self.response = self.client.get(r('importer:sales-import'))

    def test_get(self):
        """GET / must return status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'importer/salesimport_form.html')

    def test_html(self):
        """Html must contain specific input tags"""
        tags = (('<form', 1),
                ('enctype="multipart/form-data"', 1),
                ('<input', 6),
                ('type="hidden"', 1),
                ('type="text"', 1),
                ('type="date"', 1),
                ('type="file"', 1),
                ('type="submit"', 1))

        for text, count in tags:
            with self.subTest():
                self.assertContains(self.response, text, count)

    def test_csrf(self):
        """Html must contain csrf"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_has_form(self):
        """Context must have Sale Import form"""
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)


class SalesImportViewGetInvalid(TestCase):
    def setUp(self):
        self.response = self.client.get(r('importer:sales-import'))

    def test_get(self):
        """Must redirect to login page with next param"""
        expected = "{}?next={}".format(r('login'), r('importer:sales-import'))
        self.assertRedirects(self.response, expected)


class SalesImportViewPostValid(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        self.client.login(username=user.username, password='pass')
        file_path = Path('sales_imported_files/FileName.xlsx')
        data = dict(user=user.pk, company='Company Name', month='01/07/2018',
                    file=get_temporary_text_file(file_path.name))
        with mock_storage(file_path.as_posix()), mute_signals(signals.post_save):
            self.response = self.client.post(r('importer:sales-import'), data)

    def test_post(self):
        """Must redirect to same page"""
        self.assertRedirects(self.response, r('importer:sales-import'))

    def test_company_create(self):
        """Must create company if not exists"""
        self.assertTrue(Company.objects.exists())

    def test_sales_file(self):
        self.assertTrue(SalesImportFile.objects.exists())

    def test_success_message(self):
        """Must show a success message"""
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(1, len(messages))
        self.assertEqual('Arquivo adicionado! Assim que for importado você será notificado.', str(messages[0]))


class SalesImportViewPostInvalid(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        self.client.login(username=user.username, password='pass')
        self.response = self.client.post(r('importer:sales-import'), {})

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'importer/salesimport_form.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)


class SalesImportViewPostInvalidExtension(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        file = get_temporary_text_file('FileName.jpg')
        data = dict(user=user.pk, company='Company Name', month='01/07/2018', file=file)

        self.client.login(username=user.username, password='pass')
        self.response = self.client.post(r('importer:sales-import'), data)

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'importer/salesimport_form.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)

    def test_form_has_extension_error(self):
        """Must show a error message"""
        form = self.response.context['form']
        self.assertTrue(form.errors['file'][0])

    def test_form_extension_error_show_valid_extensions(self):
        """Must show a message with valid extensions"""
        form = self.response.context['form']
        error_message = form.errors['file'][0]
        valid_extensions = ['xlsx']

        for ext in valid_extensions:
            with self.subTest():
                self.assertIn(ext, error_message)


class SalesImportViewPostInvalidMounth(TestCase):
    def setUp(self):
        user = RandomUserFactory(password='pass')
        company = CompanyFactory.create(name='Company Name')
        month = date(day=1, month=7, year=2018)
        file = get_temporary_text_file("FileName.xlsx")
        data = dict(user=user.pk, company='Company Name', month='01/07/2018', file=file)

        self.client.login(username=user.username, password='pass')
        with mock_storage('sales_imported_files/FileName.xlsx'), mute_signals(signals.post_save):
            self.obj = SalesImportFileFactory.create(company=company, month=month)
            self.response = self.client.post(r('importer:sales-import'), data)

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'importer/salesimport_form.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)

    def test_form_has_already_imported_error(self):
        """Must show a error message for """
        form = self.response.context['form']
        expected = form.errors['__all__'][0]
        self.assertEqual('O arquivo do mês de Julho de 2018 já foi importado para Company Name', expected)
