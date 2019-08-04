import io

import pytest

import web.pool
import web.server


@pytest.fixture
def client():
    yield web.server.app.test_client()


@pytest.fixture
def pool():
    return web.pool.LatexPool()


@pytest.fixture
def valid_latex_file():
    return io.BytesIO(
        br"\documentclass{article}"
        br"\begin{document}"
        br"Hello, world!"
        br"\end{document}"
    )
