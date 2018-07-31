from pathlib import Path

from django.contrib import admin
from django.utils import formats
from django.utils.translation import gettext as _

from salesmanagement.importer.models import SalesImportFile


class SalesFileAdmin(admin.ModelAdmin):
    fields = ('user', 'company', 'month_year', 'status', 'file')
    list_display = ('filename', 'company', 'month_year', 'status', 'imported')
    list_filter = ('company', 'user')
    readonly_fields = ('filename', 'user', 'company', 'month_year', 'status', 'imported')
    list_select_related = ('company', 'user')

    def filename(self, obj):
        return Path(obj.file.name).name

    filename.short_description = _('Arquivo')

    def month_year(self, obj):
        month_year = formats.date_format(obj.month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return month_year

    month_year.short_description = _('mês')

    def imported(self, obj):
        return obj.status == SalesImportFile.IMPORTED

    imported.short_description = _('foi importado')
    imported.boolean = True

    def has_add_permission(self, request):
        return False


admin.site.register(SalesImportFile, SalesFileAdmin)
