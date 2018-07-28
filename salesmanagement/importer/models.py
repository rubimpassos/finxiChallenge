from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import formats
from django_extensions.db.models import TimeStampedModel

from salesmanagement.manager.models import Company


class SalesImportFile(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.DateField('Mês')
    file = models.FileField('Arquivo', upload_to='sales_imported_files',
                            validators=[FileExtensionValidator(['xlsx'])])

    class Meta:
        verbose_name = 'Arquivo Importado'
        verbose_name_plural = 'Arquivos Importados'

    def __str__(self):
        month_year = formats.date_format(self.month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return "Registro de vendas da empresa {company} do mês de {month_year}".format(
            company=self.company.name,
            month_year=month_year
        )
