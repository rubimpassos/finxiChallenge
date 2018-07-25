from celery import shared_task

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.manager.models import ProductsSale, Product, ProductCategory


@shared_task
def import_sales_task(sale_file_pk):
    sale_file = SalesImportFile.objects.get(pk=sale_file_pk)
    sales = ParserSalesXlsx(sale_file.file.path).as_data()

    for sale in sales:
        category, result = ProductCategory.objects.get_or_create(name=sale['category'])
        product, result = Product.objects.get_or_create(name=sale['product'], category=category)
        ProductsSale.objects.create(
            company=sale_file.company,
            product=product,
            sold=sale['sold'],
            cost=sale['cost'],
            total=sale['total'],
            sale_month=sale_file.month,
        )