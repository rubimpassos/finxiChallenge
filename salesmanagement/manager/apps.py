from django.apps import AppConfig


class ManagerConfig(AppConfig):
    name = 'salesmanagement.manager'
    verbose_name = 'Administração de vendas'

    def ready(self):
        import salesmanagement.manager.signals
