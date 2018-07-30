from django.contrib import admin
from django.db.models import Sum
from django.urls import reverse
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from salesmanagement.manager.inlines import ProducSalesInline, CompanyProductsInline
from salesmanagement.manager.models import Company, Product, ProductCategory, ProductsSale

admin.site.site_header = _('Administração')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name', 'products_count', 'sold_products', 'best_seller', 'related_links')
    readonly_fields = ('products_count', 'sold_products', 'best_seller', 'related_links')
    fields_related_links = ('related_link_products', 'related_link_sales')
    date_hierarchy = 'created'

    class Media:
        css = {
            "all": ("css/related_links.css",)
        }

    def products_count(self, obj):
        return obj.product_set.count()

    products_count.short_description = _('quantidade de produtos')

    def sold_products(self, obj):
        q = obj.productssale_set.all().aggregate(sold_count=Sum('sold'))
        return q['sold_count'] or 0

    sold_products.short_description = _('total de produtos vendidos')

    def best_seller(self, obj):
        product = obj.productssale_set.values('product').distinct().annotate(sold=Sum('sold')).latest('sold')
        product = Product.objects.get(pk=product['product'])
        url = reverse('admin:manager_product_change', args=(product.pk,))
        return mark_safe('<a href="{}">{}</a>'.format(url, product))

    best_seller.short_description = _('produto mais vendido')

    def related_links(self, obj):
        links = ''
        for f in self.fields_related_links:
            m = getattr(self, f, lambda n: '')
            links += m(obj)

        return mark_safe(links)

    related_links.short_description = _('relacionados')
    related_links.allow_tags = True

    @staticmethod
    def related_link_products(obj):
        url = reverse('admin:manager_product_changelist')
        lookup = f"company__id__exact={obj.pk}"
        text = "Produtos"
        return f'<a class="list_filter_link" href="{url}?{lookup}">{text}</a>'

    @staticmethod
    def related_link_sales(obj):
        url = reverse('admin:manager_productssale_changelist')
        lookup = f"company__id__exact={obj.pk}"
        text = "Vendas"
        return f'<a class="list_filter_link" href="{url}?{lookup}">{text}</a>'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = None
    date_hierarchy = 'created'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_cost', 'current_price')
    list_display_links = None
    list_filter = ('category', 'name', )
    readonly_fields = list_display+('company',)
    search_fields = ('name', 'category__name')
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


@admin.register(ProductsSale)
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
