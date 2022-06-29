import typing
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import pytest

import tailwind


@pytest.mark.parametrize(
    "build_kwargs, expected_options",
    (
        (dict(), ["--watch"]),
        (dict(input="i"), ["--input", "i", "--watch"]),
        (dict(input=Path("j")), ["--input", "j", "--watch"]),
        (dict(output="o"), ["--output", "o", "--watch"]),
        (dict(output=Path("p")), ["--output", "p", "--watch"]),
        (dict(content="c"), ["--content", "c", "--watch"]),
        (dict(postcss=False), ["--watch"]),
        (dict(postcss=True), ["--postcss", "--watch"]),
        (dict(postcss="p"), ["--postcss", "p", "--watch"]),
        (dict(postcss=Path("q")), ["--postcss", "q", "--watch"]),
        (dict(minify=False), ["--watch"]),
        (dict(minify=True), ["--minify", "--watch"]),
        (dict(config="c"), ["--config", "c", "--watch"]),
        (dict(config=Path("d")), ["--config", "d", "--watch"]),
        (dict(autoprefixer=False), ["--no-autoprefixer", "--watch"]),
        (dict(autoprefixer=True), ["--watch"]),
        (dict(poll=False), ["--watch"]),
        (dict(poll=True), ["--poll"]),
    ),
)
@mock.patch(
    "tailwind.run", return_value=CompletedProcess(args=[], returncode=0, stdout=b"")
)
def test_watch(
    fake_run: mock.Mock, build_kwargs: dict, expected_options: typing.List[str]
):
    tailwind.watch(**build_kwargs)

    args = fake_run.call_args[0][0]
    assert args[1] == "build"
    actual_options = args[2:]
    assert actual_options == expected_options
