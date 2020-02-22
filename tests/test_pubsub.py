import web.commands.pubsub
import web.db


def test_persistent_latex_file(app, session, latex_file):
    async_result = web.db.AsyncResult(
        token='test-token',
        origin_key='test/hello.latex'
    )
    app.storage.put_object(async_result.origin_key, latex_file)

    persistent_latex_file = web.commands.pubsub.PersistentLatexFile(
        klass=web.commands.pubsub.LatexFile,
        session=session,
        storage=app.storage,
        result=async_result
    )
    result = persistent_latex_file.save()

    assert result.getvalue()
    assert async_result.target_key == 'test/hello.pdf'
