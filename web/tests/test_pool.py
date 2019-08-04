

def test_pool_apply(pool, valid_latex_file):
    result_id = pool.apply(valid_latex_file.read())
    assert pool.get(result_id, wait=True)
