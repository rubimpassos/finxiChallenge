from django.urls import path

from salesmanagement.importer.views import SalesImportView

urlpatterns = [
    path('import/', SalesImportView.as_view(), name='sales-import'),
]
