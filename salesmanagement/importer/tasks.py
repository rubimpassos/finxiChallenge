from celery import shared_task

from salesmanagement.importer import models
from salesmanagement.importer.parser import ParserSalesXlsx
from salesmanagement.manager.models import ProductsSale, Product, ProductCategory


@shared_task(ignore_results=True, default_retry_delay=5*60)
def import_sales_task(sale_file_pk):
    sale_file = models.SalesImportFile.objects.get(pk=sale_file_pk)
    company = sale_file.company
    sales = ParserSalesXlsx(sale_file.file.path).as_data()

    if not sales:
        sale_file.imported_fail()
        return

    for sale in sales:
        category, result = ProductCategory.objects.get_or_create(name=sale['category'])
        product, result = Product.objects.get_or_create(name=sale['product'], category=category)

        if company not in product.company.all():
            product.company.add(company)

        sold, cost, total = sale['sold'], sale['cost'], sale['total']
        product_sale, result = ProductsSale.objects.get_or_create(
            company=company,
            product=product,
            sale_month=sale_file.month,
            defaults={'sold': sold, 'cost': cost, 'total': total}
        )

        if not result:
            product_sale.sold += sold
            product_sale.total += total
            product_sale.save()

    sale_file.imported()
