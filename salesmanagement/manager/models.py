from django.db import models
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField


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
        verbose_name = 'categoria de produto'
        verbose_name_plural = 'categorias de produtos'

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
    cost = MoneyField(_('preço de custo'), max_digits=14, decimal_places=2, default_currency='BRL')
    total = MoneyField(_('total da venda'), max_digits=14, decimal_places=2, default_currency='BRL')
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

    @property
    def price(self):
        """Sale price"""
        return self.total/self.sold

