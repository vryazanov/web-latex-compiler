import collections
import multiprocessing
import uuid
import tempfile
import zipfile
import pathlib

import latex


class NotFound(Exception):
    pass


class NotReady(Exception):
    pass


def build_pdf_from_zip(entry, bytes_):
    with zipfile.ZipFile(bytes_) as myzip:
        myzip.testzip()
        with tempfile.TemporaryDirectory() as tempdir:
            myzip.extractall(tempdir)
            entry_path = pathlib.Path(tempdir) / entry
            return latex.build_pdf(
                entry_path.open(), texinputs=[str(entry_path.parent)])


class Results(collections.UserDict):
    # TODO: Make a limit for number of stored results and expire
    # results that are keeping more than N minutes.
    pass


class LatexPool:
    def __init__(self):
        self.pool = multiprocessing.Pool(5)
        self.results = {}

    def apply(self, bytes_):
        return self.pool.apply(latex.build_pdf, args=(bytes_,))

    def apply_zip(self, entry, bytes_):
        result = self.pool.apply_async(
            build_pdf_from_zip, args=(entry, bytes_,))
        uid = uuid.uuid4().hex
        self.results[uid] = result
        return uid

    def get(self, uid, wait=False):
        result = self.results.get(uid)

        if not result:
            raise NotFound()

        if not wait and not result.ready():
            raise NotReady()

        return result.get()
