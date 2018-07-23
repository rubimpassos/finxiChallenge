from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from salesmanagement.sales.forms import SalesImportForm
from salesmanagement.sales.models import SalesFile


class SalesImportView(SuccessMessageMixin, CreateView):
    model = SalesFile
    form_class = SalesImportForm
    template_name = 'sales/salesimport_form.html'
    success_url = reverse_lazy('sales-import')
    success_message = "Arquivo adicionado! Assim que for importado você será notificado."
