from django.db import models
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(_('nome da empresa'), max_length=150, unique=True)

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def __str__(self):
        return self.name


class ProductCategory(TimeStampedModel):
    name = models.CharField(_('nome'), max_length=80)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(_('nome'), max_length=255)
    category = models.ForeignKey(ProductCategory, verbose_name=_('categoria'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.name


class ProductsSale(TimeStampedModel):
    company = models.ForeignKey(Company, verbose_name=_('empresa'), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_('produto'), on_delete=models.CASCADE)
    sold = models.IntegerField(_('unidades vendidas'))
    cost = models.FloatField(_('preço de custo'))
    total = models.FloatField(_('total da venda'))
    sale_month = models.DateField(_('mês de venda'))

    class Meta:
        verbose_name = 'vendas'
        verbose_name_plural = 'vendas'

    def __str__(self):
        month_year = formats.date_format(self.sale_month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return "[{company}]Vendas de {product} em {month_year}".format(
            company=self.company.name,
            product=self.product.name,
            month_year=month_year
        )

