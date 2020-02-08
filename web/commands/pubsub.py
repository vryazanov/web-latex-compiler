import io
import logging

import flask
import flask_script
import latex

import web.db


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


def process_async_result(session, async_result):
    async_result.generate_target_key()

    origin, target = io.BytesIO(), io.BytesIO()
    flask.current_app.storage.get_object(async_result.origin_key, origin)

    pdf = latex.build_pdf(origin.getvalue())
    pdf.save_to(target)

    target.seek(0)

    flask.current_app.storage.put_object(async_result.target_key, target)

    session.add(async_result)
    session.commit()


@PubSubCommand.option('--batch-size', type=int, required=True)
@PubSubCommand.option('--sleep', type=int, required=True)
def listen(sleep, batch_size):

    for msg in flask.current_app.message.polling(sleep, batch_size):
        logger.info(f'Received a message: {msg}.')
        async_result = web.db.AsyncResult.query.get(msg['async_result_id'])

        if not async_result:
            logger.warning('Async result instance is not found.')
            continue

        process_async_result(flask.current_app.db.session, async_result)
