from django.urls import path

from salesmanagement.sales.views import SalesImportView

urlpatterns = [
    path('import/', SalesImportView.as_view(), name='sales-import'),
]
