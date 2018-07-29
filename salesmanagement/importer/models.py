from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import formats
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django_extensions.db.models import TimeStampedModel

from salesmanagement.manager.models import Company


User = get_user_model()


class SalesImportFile(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=_('usuário que enviou'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.DateField(_l('mês'))
    file = models.FileField(_l('arquivo'), upload_to='sales_imported_files',
                            validators=[FileExtensionValidator(['xlsx'])])

    class Meta:
        verbose_name = _l('arquivo Importado')
        verbose_name_plural = _l('arquivos Importados')

    def __str__(self):
        month_year = formats.date_format(self.month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return _("Registro de vendas de {company} no mês de {month_year}".format(
            company=self.company.name,
            month_year=month_year
        ))
