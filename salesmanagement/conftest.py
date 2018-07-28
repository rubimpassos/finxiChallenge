import shutil
import tempfile

import pytest
from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import FileField


def setup_test_environment():
    """Override static storage with tempdir"""
    # Keep track of original storages.
    settings._original_media_root = settings.MEDIA_ROOT
    settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
    settings._original_fields_storages = {}

    # Creates a temporary directory.
    settings._temp_media_dir = tempfile.mkdtemp(dir=settings.BASE_DIR)

    # Use the FileSystemStorage for tests.
    settings.MEDIA_ROOT = settings._temp_media_dir
    settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    # Use the FileSystemStorage for all model fields.
    for model in apps.get_models(include_auto_created=False):
        fields = [f for f in model._meta.fields if isinstance(f, FileField)]
        for field in fields:
            model_path = '%s.%s' % (model._meta.app_label, model._meta.model_name)
            original_storage = (field.name, field.storage)
            original_storages = settings._original_fields_storages.setdefault(model_path, [])
            original_storages.append(original_storage)
            field.storage = FileSystemStorage(location=settings.MEDIA_ROOT)


def teardown_test_environment():
    """Cleanup tmpdir and restore default storage"""
    # Delete the temporary directory.
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    # Restore original storage.
    settings.MEDIA_ROOT = settings._original_media_root
    settings.DEFAULT_FILE_STORAGE = settings._original_file_storage

    # Restore original storages for all model fields.
    for model_path, original_storages in settings._original_fields_storages.items():
        model = apps.get_model(*model_path.split('.'))
        for field_name, original_storage in original_storages:
            field = model._meta.get_field(field_name)
            field.storage = original_storage

    del settings._original_media_root
    del settings._original_file_storage
    del settings._original_fields_storages


@pytest.fixture(scope='session', autouse=True)
def enviroment():
    setup_test_environment()
    yield enviroment
    teardown_test_environment()
