from django.db import models
from django_extensions.db.models import TimeStampedModel

from salesmanagement.sales.validators import validate_extension


class Company(TimeStampedModel):
    name = models.CharField('Nome da empresa', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name


class SalesImportFile(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.DateField('Mês')
    file = models.FileField('Arquivo', upload_to='sales_imported_files',
                            validators=[validate_extension(['.xls', '.xlsx', '.xlsm', '.csv'])])

    class Meta:
        verbose_name = 'Arquivo Importado'
        verbose_name_plural = 'Arquivos Importados'

    def __str__(self):
        return self.file.name
