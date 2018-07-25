from django.contrib import admin
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from salesmanagement.manager.models import ProductsSale, Product


class CompanyProductsInline(admin.TabularInline):
    model = Product.company.through
    extra = 0
    verbose_name = "Produto"
    verbose_name_plural = "Produtos"
    fields = ('product_link', 'category', 'current_cost', 'current_price')
    readonly_fields = fields
    can_delete = False

    def product_link(self, obj):
        url = reverse('admin:manager_product_change', args=(obj.product.pk,))
        return mark_safe('<a href="{}">{}</a>'.format(url, obj.product))

    product_link.short_description = _('produto')

    def category(self, obj):
        url = reverse('admin:manager_productcategory_change', args=(obj.product.category.pk,))
        return mark_safe('<a href="{}">{}</a>'.format(url, obj.product.category))

    category.short_description = _('categoria')

    def month(self, obj):
        month_year = formats.date_format(obj.sale_month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return month_year

    month.short_description = _('mês')

    def current_cost(self, obj):
        """Get last manufacturing cost in the month"""
        last_sale = obj.product.productssale_set.last()
        return getattr(last_sale, 'cost', '')

    current_cost.short_description = _('custo atual')

    def current_price(self, obj):
        """Get last sale price in the month"""
        last_sale = obj.product.productssale_set.last()
        return getattr(last_sale, 'price', '')

    current_price.short_description = _('preço de venda atual')

    def has_add_permission(self, request):
        return False


class ProducSalesInline(admin.TabularInline):
    model = ProductsSale
    extra = 0
    verbose_name = "Venda"
    verbose_name_plural = "Vendas"
    fields = ('sold', 'cost', 'price', 'total', 'month')
    readonly_fields = fields
    can_delete = False

    def price(self, obj):
        return obj.price

    price.short_description = _('preço de venda')

    def month(self, obj):
        month_year = formats.date_format(obj.sale_month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return month_year

    month.short_description = _('mês')

    def has_add_permission(self, request):
        return False
