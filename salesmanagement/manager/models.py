from django.db import models
from django_extensions.db.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField('Nome da empresa', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name
