from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import formats
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django_extensions.db.models import TimeStampedModel
from notifications.signals import notify

from salesmanagement.importer import tasks
from salesmanagement.manager.models import Company


User = get_user_model()


class SalesImportFile(TimeStampedModel):
    IMPORTED = 'IMPORTED'
    ERROR = 'ERROR'
    PROCESSING = 'PROCESSING'
    STATUS = (
        (PROCESSING, _('Em processamento')),
        (IMPORTED, _('Importado com sucesso')),
        (ERROR, _('Falha ao importar os dados, verifique o arquivo e envie-o novamente!'))
    )

    user = models.ForeignKey(User, verbose_name=_('usuário que enviou'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.DateField(_l('mês'))
    file = models.FileField(_l('arquivo'), upload_to='sales_imported_files',
                            validators=[FileExtensionValidator(['xlsx'])])
    status = models.CharField(_('status'), max_length=15, choices=STATUS, default=PROCESSING)

    __old_status = None
    __old_file = None

    class Meta:
        verbose_name = _l('arquivo Importado')
        verbose_name_plural = _l('arquivos Importados')

    def __str__(self):
        month_year = formats.date_format(self.month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return _(f'Registro de vendas de {self.company.name} do mês de {month_year}')

    def __init__(self, *args, **kwargs):
        super(SalesImportFile, self).__init__(*args, **kwargs)
        if self.pk is not None:
            self.__old_file = self.file
            self.__old_status = self.status

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.file != self.__old_file:
            tasks.import_sales_task.delay(self.pk)

        if self.__old_status != self.status:
            if self.status == self.IMPORTED:
                notify.send(self, recipient=self.user, verb=_('foi importado'))
            elif self.status == self.ERROR:
                notify.send(self, recipient=self.user, verb=_('falhou ao ser importado'))

        self.__old_file = self.file
        self.__old_status = self.status

    def imported(self):
        self.status = self.IMPORTED
        self.save()

    def imported_fail(self):
        self.status = self.ERROR
        self.save()
