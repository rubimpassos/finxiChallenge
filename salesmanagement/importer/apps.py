from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class SalesConfig(AppConfig):
    name = 'salesmanagement.importer'
    verbose_name = 'Importar arquivos de vendas'

    def ready(self):
        autodiscover_modules('receivers')
