from datetime import date

import factory
from django.db.models import signals
from factory.django import DjangoModelFactory

from salesmanagement.core.factories import RandomUserFactory
from salesmanagement.importer.models import SalesImportFile
from salesmanagement.manager.factories import CompanyFactory


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class SalesImportFileFactory(DjangoModelFactory):
    class Meta:
        model = SalesImportFile

    user = factory.SubFactory(RandomUserFactory)
    company = factory.SubFactory(CompanyFactory)
    month = date(day=1, month=7, year=2018)
    file = factory.django.FileField(data='data', filename=factory.Sequence(lambda n: "FileName_%d.xlsx" % n))
