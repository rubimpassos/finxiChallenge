import locale

from djmoney.money import Money
from openpyxl import load_workbook


class ParserSalesXlsx:
    def __init__(self, file_path, header=None):
        self.file_path = file_path
        self.header = header if header else ['product', 'category', 'sold', 'cost', 'total']
        self.max_columns = len(self.header)

    def as_data(self):
        """Returns a list with the xlsx rows, each row is a dict with cells value"""
        wb = load_workbook(filename=self.file_path)
        ws = wb.active
        data = []

        for i, row in enumerate(ws.rows):
            if len(row) != self.max_columns:
                return []

            if i == 0:
                # skip file header
                continue

            try:
                d = self.get_row_dict(row)
            except Exception:
                return []

            data.append(d)

        return data

    def get_row_dict(self, row):
        d = {}
        for i, h in enumerate(self.header):
            parser = getattr(self, 'parse_'+h, self.default_parse)
            d[h] = parser(row[i].value)

        return d

    def default_parse(self, v):
        return v

    def parse_product(self, v):
        return str(v)

    def parse_category(self, v):
        return str(v)

    def parse_sold(self, v):
        return int(v)

    def parse_cost(self, cost_string):
        return self.parse_currency(cost_string)

    def parse_total(self, total_string):
        return self.parse_currency(total_string)

    @staticmethod
    def parse_currency(currency):
        if isinstance(currency, float):
            return Money(currency, 'BRL')

        n = str(currency).replace('R$', '').strip()
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        return Money(locale.atof(n), 'BRL')
