import io
import logging
import typing

import flask
import flask_script
import latex
from sqlalchemy.orm.session import Session

import web.db
import web.storage


logger = logging.getLogger(__name__)

PubSubCommand = flask_script.Manager(help='Run latex files compilation')

# TODO: implement later
# import pathlib
# import tempfile
# import zipfile
#
# def build_pfd_from_zip(self, entrypoint: str, stream: io.RawIOBase):
#     with zipfile.ZipFile(stream) as myzip:
#         myzip.testzip()
#         with tempfile.TemporaryDirectory() as tempdir:
#             myzip.extractall(tempdir)
#             entry_path = pathlib.Path(tempdir) / entrypoint
#             return latex.build_pdf(
#                 entry_path.open(), texinputs=[str(entry_path.parent)])


class BaseLatexFile:
    def save(self) -> io.BytesIO:
        raise NotImplementedError


class LatexFile(BaseLatexFile):
    def __init__(self, stream: io.RawIOBase):
        self._stream = stream

    def save(self):
        target = io.BytesIO()
        pdf = latex.build_pdf(self._stream.getvalue())
        pdf.save_to(target)
        target.seek(0)
        return target


class LatexFileFromArchive(BaseLatexFile):
    pass


class PersistentLatexFile(BaseLatexFile):
    def __init__(
        self, klass: typing.Type[BaseLatexFile], session: Session,
        storage: web.storage.BaseStorage, result: web.db.AsyncResult
    ):
        self._klass = klass
        self._session = session
        self._storage = storage
        self._result = result

    def save(self):
        origin = io.BytesIO()
        self._storage.get_object(self._result.origin_key, origin)

        instance = self._klass(origin)
        target = instance.save()

        self._result.generate_target_key()
        self._storage.put_object(self._result.target_key, target)
        self._session.commit()
        return target


@PubSubCommand.option('--sleep', type=int, required=True)
def listen(sleep):

    for msg in flask.current_app.message.polling(sleep):
        logger.info(f'Received a message: {msg}.')
        async_result = web.db.AsyncResult.query.get(msg['async_result_id'])

        if not async_result:
            logger.warning('Async result instance is not found.')
            continue

        latex_file = PersistentLatexFile(
            klass=LatexFile,
            session=flask.current_app.db.session,
            storage=flask.current_app.storage,
            result=async_result
        )
        latex_file.save()
