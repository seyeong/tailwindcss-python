import typing
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import pytest

import tailwind

TAILWIND_CONFIG_FILE_NAME = "tailwind.config.js"
POSTCSS_CONFIG_FILE_NAME = "postcss.config.js"


@pytest.mark.parametrize(
    "init_kwargs, expected_options",
    (
        (dict(), []),
        (dict(full=True), ["--full"]),
        (dict(full=False), []),
        (dict(postcss=True), ["--postcss"]),
        (dict(postcss=False), []),
    ),
)
@mock.patch(
    "tailwind.run", return_value=CompletedProcess(args=[], returncode=0, stdout=b"")
)
def test_initz(
    fake_run: mock.Mock, init_kwargs: dict, expected_options: typing.List[str]
):
    tailwind.init(**init_kwargs)

    args = fake_run.call_args[0][0]
    assert args[1] == "init"
    actual_options = args[2:]
    assert actual_options == expected_options


@pytest.mark.parametrize(
    "init_kwargs, expected_postcss_config",
    (
        (dict(full=False, postcss=False), False),
        (dict(full=True, postcss=False), False),
        (dict(full=False, postcss=True), True),
        (dict(full=False, postcss=True), True),
    ),
)
def test_init_integration(
    cwd_tmp_path: Path, init_kwargs: dict, expected_postcss_config: bool
):
    assert not Path(TAILWIND_CONFIG_FILE_NAME).exists()
    assert not Path(POSTCSS_CONFIG_FILE_NAME).exists()

    tailwind.init(**init_kwargs)

    assert Path(TAILWIND_CONFIG_FILE_NAME).is_file()
    assert Path(POSTCSS_CONFIG_FILE_NAME).is_file() is expected_postcss_config


@pytest.mark.parametrize(
    "init_kwargs, create_file",
    (
        (dict(full=False, postcss=False), TAILWIND_CONFIG_FILE_NAME),
        (dict(full=True, postcss=False), TAILWIND_CONFIG_FILE_NAME),
        (dict(full=False, postcss=True), TAILWIND_CONFIG_FILE_NAME),
        (dict(full=False, postcss=True), POSTCSS_CONFIG_FILE_NAME),
        (dict(full=True, postcss=True), TAILWIND_CONFIG_FILE_NAME),
        (dict(full=True, postcss=True), POSTCSS_CONFIG_FILE_NAME),
    ),
)
def test_already_exists(cwd_tmp_path: Path, init_kwargs: dict, create_file: str):
    Path(create_file).touch()

    with pytest.raises(tailwind.ConfigFileExistsError) as excinfo:
        tailwind.init(**init_kwargs)
        assert create_file in str(excinfo.value)


def test_init_error():
    class MyError(Exception):
        pass

    side_effect = MyError()
    with mock.patch("tailwind.run", side_effect=side_effect) as run:
        with pytest.raises(tailwind.InitError) as excinfo:
            tailwind.init()
        assert excinfo.value.__cause__ is side_effect

    assert run.called
