import io
import os
import pathlib
import tempfile

import pytest

import web.storage


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as folder:
        yield folder


def test_fs_storage_put_object(temp_dir):
    FILENAME = 'test.txt'
    FILEBODY = b'test string'

    storage = web.storage.FileSystemStorage(temp_dir)
    storage.put_object(FILENAME, io.BytesIO(FILEBODY))

    with open(os.path.join(temp_dir, FILENAME), 'rb') as fout:
        assert fout.read() == FILEBODY


def test_fs_storage_get_object(temp_dir):
    FILENAME = 'test.txt'
    FILEBODY = b'test string'

    path = pathlib.Path(temp_dir) / FILENAME
    path.write_bytes(FILEBODY)

    with tempfile.TemporaryFile() as fileobj:
        storage = web.storage.FileSystemStorage(temp_dir)
        storage.get_object(path.name, fileobj)

        fileobj.seek(0)
        assert fileobj.read() == FILEBODY
