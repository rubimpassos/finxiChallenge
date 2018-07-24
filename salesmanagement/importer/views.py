from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from salesmanagement.importer.forms import SalesImportForm
from salesmanagement.importer.models import SalesImportFile


class SalesImportView(SuccessMessageMixin, CreateView):
    model = SalesImportFile
    form_class = SalesImportForm
    template_name = 'importer/salesimport_form.html'
    success_url = reverse_lazy('sales-import')
    success_message = "Arquivo adicionado! Assim que for importado você será notificado."
