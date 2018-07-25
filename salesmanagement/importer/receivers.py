from django.db.models.signals import post_save
from django.dispatch import receiver

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.tasks import import_sales_task


@receiver(post_save, sender=SalesImportFile, dispatch_uid='post_save_sales_import_file')
def post_save_sales_import_file(sender, instance, **kwargs):
    import_sales_task.delay(instance.pk)
