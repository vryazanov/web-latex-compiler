import io
import os
import pathlib
import shutil

from google.cloud import storage


class BaseStorage:
    def get_object(self, key, fileobj):
        raise NotImplementedError

    def put_object(self, key, fileobj):
        raise NotImplementedError


class CloudStorage(BaseStorage):
    """Storage to work with Google Cloud Storage"""

    def __init__(self, bucket_name: str):
        self._storage = storage.Client()
        self._bucket = self._storage.bucket(bucket_name)

    def get_object(self, key: str, fileobj: io.BufferedIOBase):
        blob = self._bucket.get_blob(key)
        blob.download_to_file(fileobj)

    def put_object(self, key: str, fileobj: io.RawIOBase):
        blob = storage.Blob(key, self._bucket)
        blob.upload_from_file(fileobj)


class FileSystemStorage(BaseStorage):
    """It allows to keep files in local FS"""

    def __init__(self, media_root: str):
        self._media_root = pathlib.Path(media_root)
        if not self._media_root.exists():
            self._media_root.mkdir()

    def get_object(self, key: str, fileobj: io.BufferedIOBase):
        with (self._media_root / key).open('rb') as fout:
            shutil.copyfileobj(fout, fileobj)

    def put_object(self, key: str, fileobj: io.RawIOBase):
        folder = self._media_root / os.path.dirname(key)

        if not folder.exists():
            folder.mkdir()

        filepath = folder / os.path.basename(key)

        with filepath.open('wb') as fin:
            shutil.copyfileobj(fileobj, fin)
