import json
import logging
import os
import shutil
import sys
import typing
from contextlib import contextmanager
from pathlib import Path

from cookiecutter.main import cookiecutter
from requests import Session

logger = logging.getLogger(__name__)

GITHUB_API = Session()
GITHUB_API.headers["accept"] = "application/vnd.github.v3+json"


class ReleaseAsset(typing.TypedDict):
    browser_download_url: str
    name: str
    size: int
    ...


class Release(typing.TypedDict):
    html_url: str
    tag_name: str
    name: str
    body: str
    assets: typing.List[ReleaseAsset]
    ...


def create_build_dir() -> Path:
    build_dir = Path(__file__).resolve().parent.joinpath("build")
    build_dir.mkdir(exist_ok=True)

    return build_dir


PLATFORM_TAG = {
    "windows-x64.exe": "win_amd64",
    "macos-x64": "macosx_10_9_x86_64",
    "macos-arm64": "macosx_11_0_arm64",
    "linux-x64": "manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64",
    "linux-arm64": "manylinux_2_17_aarch64.manylinux2014_aarch64.manylinux_2_24_aarch64",
}


def build(
    build_dir: Path, cache_dir: Path, wheel_dir: Path, tag: str, pre_release: str
) -> None:
    response = GITHUB_API.get(
        f"https://api.github.com/repos/tailwindlabs/tailwindcss/releases/tags/{tag}"
    )
    response.raise_for_status()
    release: Release = response.json()

    release_cache_dir = cache_dir.joinpath(tag)
    release_cache_dir.mkdir(parents=True, exist_ok=True)

    version = tag[1:] + pre_release
    output_dir = wheel_dir.joinpath(version)

    for asset in release["assets"]:
        logger.info(f"Processing {asset['name']}.")

        asset_path = release_cache_dir.joinpath(asset["name"])
        download = True
        if asset_path.is_file():
            size = asset_path.stat().st_size
            if size != asset["size"]:
                logger.debug(
                    "Cached asset at %s is invalid. Expecting %i bytes but got %i instead. Deleting the cache.",
                    asset_path,
                    asset["size"],
                    size,
                )
                asset_path.unlink()
            else:
                logger.debug(
                    "Cached asset exists at %s. Using the cache instead.", asset_path
                )
                download = False

        if download:
            logger.info("Downloading %s", asset_path.relative_to(cache_dir))

            response = GITHUB_API.get(asset["browser_download_url"], stream=True)
            response.raw.decode_content = True
            with asset_path.open("wb") as fp:
                shutil.copyfileobj(response.raw, fp)

            logger.info("Saved the asset at %s", asset_path)

        os.chmod(asset_path, 0o755)
        bin = asset_path.resolve()
        tailwind_platform = bin.name.split("-", 1)[1]
        platform = PLATFORM_TAG[tailwind_platform]
        project_slug = f"tailwind-{platform}"

        with cookiecutter_context(
            {
                "project_slug": project_slug,
                "tag": tag,
                "platform": platform,
                "version": version,
                "bin_basename": bin.name,
                "bin": str(bin),
            }
        ):
            cookiecutter(
                template=str(build_dir.parent),
                output_dir=output_dir,
                overwrite_if_exists=True,
                no_input=True,
            )

        output_bin_dir = output_dir.joinpath(project_slug, "tailwind", "bin")
        output_bin_dir.mkdir(exist_ok=True)
        shutil.copyfile(bin, output_bin_dir.joinpath(bin.name))


@contextmanager
def cookiecutter_context(
    context: typing.Dict[str, typing.Any]
) -> typing.Generator[typing.Dict[str, typing.Any], None, None]:
    path = Path("cookiecutter.json")
    with path.open("w") as fp:
        json.dump(context, fp)

    yield context

    path.unlink()


def main() -> None:
    build_dir = create_build_dir()
    cache_dir = build_dir.joinpath("cache")
    wheel_dir = build_dir.joinpath("wheel")
    version = sys.argv[1]
    try:
        pre_release = sys.argv[2]
    except IndexError:
        pre_release = ""

    build(build_dir, cache_dir, wheel_dir, f"v{version}", pre_release)


if __name__ == "__main__":
    main()
