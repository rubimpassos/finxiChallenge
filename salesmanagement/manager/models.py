from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField('Nome da empresa', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name


class ProductCategory(TimeStampedModel):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(_('Nome'), max_length=255)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductsSale(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sold = models.IntegerField(_('Unidades Vendidas'))
    cost = models.FloatField(_('Preço de Custo'))
    total = models.FloatField(_('Total da venda'))
    sale_month = models.DateField(_('Mês de venda'))

