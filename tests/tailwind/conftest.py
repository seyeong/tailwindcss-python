import os
from pathlib import Path

import pytest


@pytest.fixture
def cwd_tmp_path(tmp_path):
    cwd = Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(cwd)
