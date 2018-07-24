from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


def validate_extension(extensions):
    return FileExtensionValidator(
        extensions,
        _('Arquivo não suportado. Extensões válidas: {}'.format(', '.join(extensions)))
    )
