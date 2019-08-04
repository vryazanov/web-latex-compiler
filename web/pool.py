import multiprocessing
import uuid

import latex


class NotFound(Exception):
    pass


class NotReady(Exception):
    pass


class LatexPool:
    def __init__(self):
        self.mapping = {}
        self.pool = multiprocessing.Pool(5)

    def apply(self, bytes_):
        result = self.pool.apply_async(latex.build_pdf, args=(bytes_,))
        uid = uuid.uuid4().hex
        self.mapping[uid] = result
        return uid

    def get(self, uid, wait=False):
        result = self.mapping.get(uid)

        if not result:
            raise NotFound()

        if not wait and not result.ready():
            raise NotReady()

        return result.get()
