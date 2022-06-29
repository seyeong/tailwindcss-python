import typing
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import pytest

import tailwind


def test_build_integration():
    output = tailwind.build()
    assert output.startswith("/*")


@pytest.mark.parametrize(
    "build_kwargs, expected_options",
    (
        (dict(), []),
        (dict(input="i"), ["--input", "i"]),
        (dict(input=Path("j")), ["--input", "j"]),
        (dict(output="o"), ["--output", "o"]),
        (dict(output=Path("p")), ["--output", "p"]),
        (dict(content="c"), ["--content", "c"]),
        (dict(postcss=False), []),
        (dict(postcss=True), ["--postcss"]),
        (dict(postcss="p"), ["--postcss", "p"]),
        (dict(postcss=Path("q")), ["--postcss", "q"]),
        (dict(minify=False), []),
        (dict(minify=True), ["--minify"]),
        (dict(config="c"), ["--config", "c"]),
        (dict(config=Path("d")), ["--config", "d"]),
        (dict(autoprefixer=False), ["--no-autoprefixer"]),
        (dict(autoprefixer=True), []),
    ),
)
@mock.patch(
    "tailwind.run", return_value=CompletedProcess(args=[], returncode=0, stdout=b"")
)
def test_build(
    fake_run: mock.Mock, build_kwargs: dict, expected_options: typing.List[str]
):
    tailwind.build(**build_kwargs)

    args = fake_run.call_args[0][0]
    assert args[1] == "build"
    actual_options = args[2:]
    assert actual_options == expected_options
