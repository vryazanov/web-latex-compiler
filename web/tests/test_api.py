import functools

import web.pool


def test_upload_simple(client, latex_file):
    data = {'file': (latex_file, 'test.latex')}
    response = client.post(
        '/upload', data=data, content_type='multipart/form-data')
    assert response.data


def test_upload_large(monkeypatch, client, latex_zip):
    # Patch `get` method to process latex files synchroniously
    patched_get = functools.partialmethod(web.pool.LatexPool.get, wait=True)
    monkeypatch.setattr(web.pool.LatexPool, 'get', patched_get)

    entry, bytes_ = latex_zip
    data = {'file': (bytes_, 'test.latex'), 'entry': entry}
    response = client.post(
        '/upload-zip', data=data, content_type='multipart/form-data')

    response = client.get('/result/' + response.json['result_id'])
    assert response.data
