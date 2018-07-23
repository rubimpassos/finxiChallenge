import os
from io import StringIO
from unittest import mock

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile


def get_temporary_text_file(file_name):
    io = StringIO()
    io.write('File Content')
    io.seek(0, os.SEEK_END)
    text_file = InMemoryUploadedFile(io, None, file_name, 'text', io.tell(), None)
    text_file.seek(0)
    return text_file


def mock_storage(file_path):
    mock_save = mock.MagicMock(return_value=file_path)
    storage_mock = mock.patch.object(FileSystemStorage, '_save', mock_save)

    return storage_mock
