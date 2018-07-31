from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from django.urls import reverse
from django.utils import formats
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from salesmanagement.manager.inlines import ProductSalesInline
from salesmanagement.manager.models import Company, Product, ProductCategory, ProductsSale

admin.site.site_header = _('Administração')


class ChangeListCustomLookup(ChangeList):
    ignore_lookups = ('_disable_filters',)

    def get_filters_params(self, params=None, skipp_ignore=False):
        lookup_params = super().get_filters_params(params=params)
        if skipp_ignore:
            return lookup_params

        for ignored in self.ignore_lookups:
            if ignored in lookup_params:
                del lookup_params[ignored]
        return lookup_params


class ModelAdminCompanyFilter(admin.ModelAdmin):
    request = None

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.request = request
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context=extra_context)

    def get_changelist(self, request, **kwargs):
        return ChangeListCustomLookup

    def get_queryset(self, request):
        q = super().get_queryset(request)
        company_id = self.get_company_id()
        if company_id is None:
            return q

        return q.filter(company__id__exact=company_id)

    def get_list_filter(self, request):
        d_filters = self.request.GET.get('_disable_filters', [])
        list_filter = [f for f in self.list_filter if f not in d_filters]
        return list_filter

    def get_company_id(self):
        company_id = self.request.GET.get('company__id__exact')
        if company_id:
            return company_id

        changelist_filters = self.request.GET.get('_changelist_filters')
        lookup_filters = {}
        if changelist_filters:
            lookup_filters = dict(param.split('=') for param in changelist_filters.split('&'))

        return lookup_filters.get('company__id__exact')


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
        if not obj.pk:
            return 0
        return obj.product_set.count() or 0

    products_count.short_description = _('quantidade de produtos')

    def sold_products(self, obj):
        q = obj.productssale_set.all().aggregate(sold_count=Sum('sold'))
        return q['sold_count'] or 0

    sold_products.short_description = _('total de produtos vendidos')

    def best_seller(self, obj):
        product = obj.productssale_set.values('product').distinct().annotate(sold=Sum('sold')).latest('sold')
        product = Product.objects.get(pk=product['product'])
        link = self.admin_link(obj, 'product', 'change', product, class_='model_change_link', args=(product.pk,))
        return mark_safe(link)

    best_seller.short_description = _('produto mais vendido')

    def related_links(self, obj):
        if not obj.pk:
            return ''
        links = ''
        for f in self.fields_related_links:
            m = getattr(self, f, lambda n: '')
            links += m(obj)

        return mark_safe(links)

    related_links.short_description = _('relacionados')
    related_links.allow_tags = True

    def related_link_products(self, obj):
        return self.admin_link(obj, 'product', 'changelist', _('Produtos'), disable_company=True)

    def related_link_sales(self, obj):
        return self.admin_link(obj, 'productssale', 'changelist', _('Vendas'), disable_company=True)

    @staticmethod
    def admin_link(obj, model, view, text, disable_company=False, class_='list_filter_link', args=None):
        filters = f'company__id__exact={obj.pk}'
        if disable_company:
            filters += '&_disable_filters=company'

        if view == 'change':
            filters = urlencode({'_changelist_filters': filters})

        url = reverse(f'admin:manager_{model}_{view}', args=args)
        return f'<a class="{class_}" href="{url}?{filters}">{text}</a>'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = None
    date_hierarchy = 'created'

    class Media:
        js = ('js/list_filter_collapse.js',)


@admin.register(Product)
class ProductAdmin(ModelAdminCompanyFilter):
    list_display = ('name', 'category', 'current_cost', 'current_price')
    list_filter = ('company', 'category', 'name')
    list_select_related = ('category',)
    fields = list_display
    readonly_fields = list_display
    search_fields = ('name', 'category__name')
    date_hierarchy = 'created'
    inlines = [ProductSalesInline]

    class Media:
        js = ('js/list_filter_collapse.js',)

    def current_cost(self, obj):
        """Get last manufacturing cost in the month"""
        q = self.get_productssale_for_company(obj).last()
        return getattr(q, 'cost', '')

    current_cost.short_description = _('custo atual')

    def current_price(self, obj):
        """Get last sale price in the month"""
        q = self.get_productssale_for_company(obj).last()
        return getattr(q, 'price', '')

    current_price.short_description = _('preço de venda atual')

    def get_productssale_for_company(self, obj):
        company_id = self.get_company_id()
        q = obj.productssale_set.all()
        if company_id:
            q = q.filter(company=company_id)

        return q


@admin.register(ProductsSale)
class ProductsSaleAdmin(ModelAdminCompanyFilter):
    list_display = ('company', 'product', 'category', 'sold', 'cost', 'price', 'total', 'month_year')
    readonly_fields = list_display
    list_filter = ('company', 'product__category', 'product')
    list_display_links = None
    search_fields = ('company__name', 'product__name', 'product__category__name', 'sold', 'cost', 'sale_month')
    date_hierarchy = 'created'

    class Media:
        js = ('js/list_filter_collapse.js',)

    def category(self, obj):
        return obj.product.category.name

    category.short_description = _('categoria')

    def month_year(self, obj):
        month_year = formats.date_format(obj.sale_month, format="YEAR_MONTH_FORMAT", use_l10n=True)
        return month_year

    month_year.short_description = _('mês')

    def price(self, obj):
        return obj.price

    price.short_description = _('preço de venda')

    def has_add_permission(self, request):
        return False
