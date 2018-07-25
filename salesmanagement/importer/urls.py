from django.urls import path

from salesmanagement.importer.views import SalesImportView

app_name = 'importer'
urlpatterns = [
    path('import/', SalesImportView.as_view(), name='sales-import'),
]
