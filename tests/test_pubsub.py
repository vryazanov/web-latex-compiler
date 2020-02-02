import io

import latex

import web.commands.pubsub
import web.db


def test_async_result_processing(app, session, latex_file):
    async_result = web.db.AsyncResult(
        token='test-token',
        origin_key='test/hello.txt'
    )
    app.storage.put_object(async_result.origin_key, latex_file)

    web.commands.pubsub.process_async_result(session, async_result)

    result = io.BytesIO()
    app.storage.get_object(async_result.target_key, result)

    assert result.getvalue()
    assert async_result.target_key == 'test/hello.txt.pdf'
