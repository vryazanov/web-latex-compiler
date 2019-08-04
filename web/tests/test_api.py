import functools

import web.pool


def test_upload_simple(client, valid_latex_file):
    data = {'file': (valid_latex_file, 'test.latex')}
    response = client.post(
        '/upload', data=data, content_type='multipart/form-data')
    assert response.data


def test_upload_large(monkeypatch, client, valid_latex_file):
    # Patch `get` method to process latex files synchroniously
    patched_get = functools.partialmethod(web.pool.LatexPool.get, wait=True)
    monkeypatch.setattr(web.pool.LatexPool, 'get', patched_get)
    data = {'file': (valid_latex_file, 'test.latex')}
    response = client.post(
        '/upload-zip', data=data, content_type='multipart/form-data')
    response = client.get('/result/' + response.json['result_id'])
    assert response.data
