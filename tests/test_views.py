import tempfile

import web.db


def test_upload(app, client, latex_file):
    data = {'file': (latex_file, 'test.latex')}
    response = client.post(
        '/upload', data=data, content_type='multipart/form-data')
    async_result = web.db.AsyncResult.query.first()
    assert response.data.decode().endswith(async_result.token)


def test_result_wrong_token(app, client):
    response = client.get('/result/test-token')
    assert response.status_code == 404


def test_result_not_processed(app, client, session):
    async_result = web.db.AsyncResult(
        token='test-token', origin_key='/report.latex')
    session.add(async_result)
    session.commit()

    response = client.get(f'/result/{async_result.token}')
    assert response.status_code == 102


def test_result_processed(app, client, session):
    filebody = b'Test data'
    with tempfile.TemporaryFile() as pdf:
        pdf.write(filebody)
        pdf.seek(0)

        app.storage.put_object('/results/target.txt', pdf)

        async_result = web.db.AsyncResult(
            token='test-token-1',
            origin_key='/results/origin.txt',
            target_key='/results/target.txt',
        )
        session.add(async_result)
        session.commit()

        response = client.get(f'/result/{async_result.token}')
        assert response.data == filebody
