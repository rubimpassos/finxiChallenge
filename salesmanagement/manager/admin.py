from django.contrib import admin
from salesmanagement.manager.models import Company


class CompanyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Company, CompanyAdmin)
