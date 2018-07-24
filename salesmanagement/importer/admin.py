from django.contrib import admin

from salesmanagement.importer.models import SalesImportFile


class SalesFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(SalesImportFile, SalesFileAdmin)
