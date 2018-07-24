import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_extension(extensions):
    def inner(value):
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in extensions:
            raise ValidationError(_('Arquivo não suportado. Extensões válidas: {}'.format(', '.join(extensions))))

    return inner
