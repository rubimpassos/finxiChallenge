import factory
from django.db.models import signals
from factory.django import DjangoModelFactory

from salesmanagement.manager.models import Company, Product, ProductCategory, ProductsSale


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: "Company Name %d" % n)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class ProductCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ProductCategory


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: "product %d" % n)
    category = factory.SubFactory(ProductCategoryFactory)

    @factory.post_generation
    def companies(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for company in extracted:
                self.company.add(company)


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class ProductsSaleFactory(DjangoModelFactory):
    class Meta:
        model = ProductsSale
