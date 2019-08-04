

def test_pool_apply(pool, latex_file):
    assert pool.apply(latex_file.read())


def test_pool_apply_zip(pool, latex_zip):
    entry, zip_ = latex_zip
    result_id = pool.apply_zip(entry, zip_)
    assert pool.get(result_id, wait=True)
