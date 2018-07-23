from datetime import date
from pathlib import Path

from django.contrib.messages import get_messages
from django.shortcuts import resolve_url as r
from django.test import TestCase

from salesmanagement.sales.forms import SalesImportForm
from salesmanagement.sales.models import SalesFile, Company
from salesmanagement.sales.tests import get_temporary_text_file, mock_storage


class SalesImportViewGet(TestCase):
    def setUp(self):
        self.response = self.client.get(r('sales-import'))

    def test_get(self):
        """GET / must return status code 200"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'sales/salesimport_form.html')

    def test_html(self):
        """Html must contain specific input tags"""
        tags = (('<form', 1),
                ('enctype="multipart/form-data"', 1),
                ('<input', 5),
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


class SalesImportViewPostValid(TestCase):
    def setUp(self):
        file_path = Path('sales_imported_files/FileName.xlsx')
        data = dict(company='Company Name', month='01/07/2018', file=get_temporary_text_file(file_path.name))
        with mock_storage(file_path.as_posix()):
            self.response = self.client.post(r('sales-import'), data)

    def test_post(self):
        """Must redirect to same page"""
        self.assertRedirects(self.response, r('sales-import'))

    def test_company(self):
        self.assertTrue(Company.objects.exists())

    def test_sales_file(self):
        self.assertTrue(SalesFile.objects.exists())

    def test_success_message(self):
        """Must show a success message"""
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(1, len(messages))
        self.assertEqual('Arquivo adicionado! Assim que for importado você será notificado.', str(messages[0]))


class SalesImportViewPostInvalid(TestCase):
    def setUp(self):
        self.response = self.client.post(r('sales-import'), {})

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'sales/salesimport_form.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)


class SalesImportViewPostInvalidExtension(TestCase):
    def setUp(self):
        file_path = Path('sales_imported_files/FileName.jpg')
        data = dict(company='Company Name', month='01/07/2018', file=get_temporary_text_file(file_path.name))
        with mock_storage(file_path.as_posix()):
            self.response = self.client.post(r('sales-import'), data)

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'sales/salesimport_form.html')

    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)

    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SalesImportForm)

    def test_form_has_extension_error(self):
        """Must show a error message with valid extensions"""
        form = self.response.context['form']
        expected = form.errors['file'][0]
        self.assertEqual('Arquivo não suportado. Extensões válidas: .xls, .xlsx, .xlsm, .csv', expected)


class SalesImportViewPostInvalidMounth(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Company Name')
        month = date(day=1, month=7, year=2018)
        file = get_temporary_text_file("FileName.xlsx")
        data = dict(company='Company Name', month='01/07/2018', file=file)

        with mock_storage('sales_imported_files/FileName.xlsx'):
            self.obj = SalesFile.objects.create(company=company, file=file, month=month)
            self.response = self.client.post(r('sales-import'), data)

    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use salesimport_form.html"""
        self.assertTemplateUsed(self.response, 'sales/salesimport_form.html')

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
