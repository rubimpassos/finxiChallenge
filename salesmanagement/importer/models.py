from django.core.validators import FileExtensionValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

from salesmanagement.manager.models import Company


class SalesImportFile(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.DateField('Mês')
    file = models.FileField('Arquivo', upload_to='sales_imported_files',
                            validators=[FileExtensionValidator(['xls', 'xlsx', 'xlsm', 'csv'])])

    class Meta:
        verbose_name = 'Arquivo Importado'
        verbose_name_plural = 'Arquivos Importados'

    def __str__(self):
        return self.file.name
