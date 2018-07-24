from django.contrib import admin

from salesmanagement.sales.models import Company, SalesImportFile


class CompanyAdmin(admin.ModelAdmin):
    pass


class SalesFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Company, CompanyAdmin)
admin.site.register(SalesImportFile, SalesFileAdmin)
