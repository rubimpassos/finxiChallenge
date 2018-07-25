from datetime import date
from pathlib import Path

from django.contrib.messages import get_messages
from django.shortcuts import resolve_url as r

from salesmanagement.importer.forms import SalesImportForm
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.manager.models import Company
from salesmanagement.importer.tests import get_temporary_text_file, mock_storage, NoImportSalesSignalsTestCase


class SalesImportViewGet(NoImportSalesSignalsTestCase):
    def setUp(self):
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


class SalesImportViewPostValid(NoImportSalesSignalsTestCase):
    def setUp(self):
        file_path = Path('sales_imported_files/FileName.xlsx')
        data = dict(company='Company Name', month='01/07/2018', file=get_temporary_text_file(file_path.name))
        with mock_storage(file_path.as_posix()):
            self.response = self.client.post(r('importer:sales-import'), data)

    def test_post(self):
        """Must redirect to same page"""
        self.assertRedirects(self.response, r('importer:sales-import'))

    def test_company(self):
        self.assertTrue(Company.objects.exists())

    def test_sales_file(self):
        self.assertTrue(SalesImportFile.objects.exists())

    def test_success_message(self):
        """Must show a success message"""
        messages = list(get_messages(self.response.wsgi_request))
        self.assertEqual(1, len(messages))
        self.assertEqual('Arquivo adicionado! Assim que for importado você será notificado.', str(messages[0]))


class SalesImportViewPostInvalid(NoImportSalesSignalsTestCase):
    def setUp(self):
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


class SalesImportViewPostInvalidExtension(NoImportSalesSignalsTestCase):
    def setUp(self):
        file_path = Path('sales_imported_files/FileName.jpg')
        data = dict(company='Company Name', month='01/07/2018', file=get_temporary_text_file(file_path.name))
        with mock_storage(file_path.as_posix()):
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


class SalesImportViewPostInvalidMounth(NoImportSalesSignalsTestCase):
    def setUp(self):
        company = Company.objects.create(name='Company Name')
        month = date(day=1, month=7, year=2018)
        file = get_temporary_text_file("FileName.xlsx")
        data = dict(company='Company Name', month='01/07/2018', file=file)

        with mock_storage('sales_imported_files/FileName.xlsx'):
            self.obj = SalesImportFile.objects.create(company=company, file=file, month=month)
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
