from django.contrib import admin
from django.utils import formats
from django.utils.translation import gettext_lazy as _

from salesmanagement.manager.inlines import ProducSalesInline, CompanyProductsInline
from salesmanagement.manager.models import Company, Product, ProductCategory, ProductsSale


class CompanyAdmin(admin.ModelAdmin):
    inlines = [CompanyProductsInline]
    date_hierarchy = 'created'


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = None
    date_hierarchy = 'created'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_cost', 'current_price')
    list_display_links = None
    readonly_fields = list_display+('company',)
    date_hierarchy = 'created'
    inlines = [ProducSalesInline]

    def current_cost(self, obj):
        """Get last manufacturing cost in the month"""
        last_sale = obj.productssale_set.last()
        return getattr(last_sale, 'cost', '')

    current_cost.short_description = _('custo atual')

    def current_price(self, obj):
        """Get last sale price in the month"""
        last_sale = obj.productssale_set.last()
        return getattr(last_sale, 'price', '')

    current_price.short_description = _('preço de venda atual')


class ProductsSaleAdmin(admin.ModelAdmin):
    list_display = ('company', 'product', 'category', 'sold', 'cost', 'price', 'total', 'month')
    list_filter = ('company', 'product__category', 'product')
    list_display_links = None
    search_fields = ('company__name', 'product__name', 'product__category__name', 'sold', 'cost', 'sale_month')
    date_hierarchy = 'created'

    class Media:
        js = ('js/list_filter_collapse.js',)

    def category(self, obj):
        return obj.product.category.name

    category.short_description = _('categoria')

    def month(self, obj):
        month_year = formats.date_format(obj.sale_month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return month_year

    month.short_description = _('mês')

    def price(self, obj):
        return obj.price

    price.short_description = _('preço de venda')


admin.site.register(Company, CompanyAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductsSale, ProductsSaleAdmin)
