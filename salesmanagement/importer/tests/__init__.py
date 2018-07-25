import os
from io import StringIO
from unittest import mock

import pytest
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.test import TestCase

from salesmanagement.importer.models import SalesImportFile
from salesmanagement.importer.receivers import post_save_sales_import_file


def get_temporary_text_file(file_name, content='File Content'):
    io = StringIO()
    io.write(content)
    io.seek(0, os.SEEK_END)
    text_file = InMemoryUploadedFile(io, None, file_name, 'text', io.tell(), None)
    text_file.seek(0)
    return text_file


def mock_storage(file_path):
    mock_save = mock.MagicMock(return_value=file_path)
    storage_mock = mock.patch.object(FileSystemStorage, '_save', mock_save)

    return storage_mock


class NoImportSalesSignalsTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def disconnect_import_sales_receiver(self):
        with DisconnectSignals(post_save, post_save_sales_import_file, SalesImportFile,
                               dispatch_uid='post_save_sales_import_file'):
            yield self.disconnect_import_sales_receiver


class DisconnectSignals(object):
    """ Temporarily disconnect a model from a signal """
    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid
        )

    def __exit__(self, type_, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False
        )
