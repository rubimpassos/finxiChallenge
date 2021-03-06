from unittest.mock import patch

from django.test import TestCase
from djmoney.money import Money

from salesmanagement.importer.parser import ParserSalesXlsx


class Cell:
    def __init__(self, value):
        self.value = value


class ParserSalesXlsxTestValid(TestCase):
    def setUp(self):
        header = [(Cell('Product'), Cell('Category'), Cell('Sold'), Cell('Cost'), Cell('Total'))]
        rows = header + [
            (Cell('Product Low'), Cell('Category A'), Cell('9'), Cell('R$ 4,70'), Cell('R$ 47,30')),
            (Cell('Product High'), Cell('Category B'), Cell('5'), Cell('R$ 3,20'), Cell('R$ 107,50'))
        ]

        with patch('salesmanagement.importer.parser.load_workbook') as mock:
            mock.return_value.active.rows = rows
            self.parser = ParserSalesXlsx('FileName.xlsx')
            self.data = self.parser.as_data()

    def test_header(self):
        """Must have specific header"""
        expected = ['product', 'category', 'sold', 'cost', 'total']
        self.assertEqual(self.parser.header, expected)

    def test_max_columns(self):
        """Max columns must be 5"""
        self.assertEqual(5, self.parser.max_columns)

    def test_parse_product_type(self):
        self.assertIsInstance(self.parser.parse_product('Product Low'), str)

    def test_parse_category_type(self):
        self.assertIsInstance(self.parser.parse_category('Category A'), str)

    def test_parse_sold_type(self):
        self.assertIsInstance(self.parser.parse_sold(9), int)

    def test_parse_currency_str(self):
        currency_float = self.parser.parse_currency('R$ 45,30')
        expected = Money(45.3, 'BRL')
        self.assertEqual(expected, currency_float)

    def test_parse_currency_int(self):
        currency_float = self.parser.parse_currency(45)
        expected = Money(45, 'BRL')
        self.assertEqual(expected, currency_float)

    def test_parse_currency_float(self):
        currency_float = self.parser.parse_currency(45.3)
        expected = Money(45.3, 'BRL')
        self.assertEqual(expected, currency_float)

    def test_output_list(self):
        expected = [
            {'product': 'Product Low', 'category': 'Category A', 'sold': 9, 'cost': Money(4.7, 'BRL'),
             'total': Money(47.3, 'BRL')},
            {'product': 'Product High', 'category': 'Category B', 'sold': 5, 'cost': Money(3.2, 'BRL'),
             'total': Money(107.5, 'BRL')}
        ]
        self.assertEqual(expected, self.data)


class ParserSalesXlsxTestInvalid(TestCase):
    def setUp(self):
        self.parser = ParserSalesXlsx('FileName.xlsx')

    def test_inconsistent_columns(self):
        """Must be empty if any error"""
        rows = [(Cell('Product High'), Cell('Category B'), Cell('5'))]
        self.assertFalse(self.get_parse_as_data(rows))

    def test_inconsistent_rows_data(self):
        """Must be empty if any error"""
        rows = [
            (Cell('Product'), Cell('Category'), Cell('Sold'), Cell('Cost'), Cell('Total')),
            (Cell('Product Low'), Cell('Category A'), Cell('9'), Cell(None), Cell('R$ 47,30')),
            (Cell('Product High'), Cell('Category B'), Cell('5'), Cell('R$ 3,20'), Cell('R$ 107,50'))
        ]
        self.assertFalse(self.get_parse_as_data(rows))

    def test_parse_sold_invalid_type(self):
        with self.assertRaises(ValueError):
            self.parser.parse_sold('a')

    def test_parse_currency_to_float_invalid(self):
        currency_float = self.parser.parse_currency('R$ 45.30')
        expected = 45.3
        self.assertNotEqual(expected, currency_float)

    def get_parse_as_data(self, rows):
        with patch('salesmanagement.importer.parser.load_workbook') as mock:
            mock.return_value.active.rows = rows
            return self.parser.as_data()
