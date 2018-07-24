from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField
from django.forms.widgets import DateInput
from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from salesmanagement.importer.models import Company, SalesImportFile


class SalesImportForm(ModelForm):
    company = CharField(label=_('Nome da Empresa'), max_length=150, required=True)

    class Meta:
        model = SalesImportFile
        fields = ('month', 'file')
        widgets = {
            'month': DateInput(attrs={'type': 'date'})
        }

    def clean_company(self):
        name = self.cleaned_data['company']
        company = Company.objects.filter(name=name).first()
        if not company:
            company = Company(name=self.cleaned_data['company'])

        return company

    def clean(self):
        cleaned_data = super(SalesImportForm, self).clean()

        company = cleaned_data.get('company')
        if not company or company.pk is None:
            return

        month = cleaned_data['month']
        files = SalesImportFile.objects.filter(month__month=month.month, month__year=month.year, company=company)
        if files.exists():
            date = formats.date_format(month, format="YEAR_MONTH_FORMAT", use_l10n=True)
            raise ValidationError(_('O arquivo do mês de {} já foi importado para {}'.format(date, company)))

        return cleaned_data

    def save(self, commit=True):
        company = self.cleaned_data['company']
        if company.pk is None:
            company.save()

        self.instance.company = company
        return super(SalesImportForm, self).save()
