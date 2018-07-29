from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from salesmanagement.importer.forms import SalesImportForm
from salesmanagement.importer.models import SalesImportFile


@method_decorator(login_required, name='dispatch')
class SalesImportView(SuccessMessageMixin, CreateView):
    model = SalesImportFile
    form_class = SalesImportForm
    template_name = 'importer/salesimport_form.html'
    success_url = reverse_lazy('importer:sales-import')
    success_message = "Arquivo adicionado! Assim que for importado você será notificado."
