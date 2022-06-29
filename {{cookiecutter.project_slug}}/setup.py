#!/usr/bin/env python

"""The setup script."""

import zipfile

from setuptools import setup
from wheel import bdist_wheel

import tailwind


class WheelFile(bdist_wheel.WheelFile):
    def writestr(
        self, zinfo_or_arcname: zipfile.ZipInfo, data: bytes, compress_type=None
    ):
        if zinfo_or_arcname.filename.endswith(tailwind._RELATIVE_TAIWIND_BIN):
            zinfo_or_arcname.external_attr = 0o100755 << 16

        super().writestr(zinfo_or_arcname, data, compress_type)


bdist_wheel.WheelFile = WheelFile


class custom_bdist_wheel(bdist_wheel.bdist_wheel):
    def get_tag(self):
        return ("py3", "none", "{{ cookiecutter.platform }}")


setup(
    author=tailwind.__author__,
    author_email=tailwind.__author_email__,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description=tailwind.__doc__,
    entry_points={
        "console_scripts": [
            "tailwindcss=tailwind:main",
        ],
    },
    keywords=["tailwind", "tailwindcss"],
    name=tailwind.__name__,
    version=tailwind.__version__,
    packages=["tailwind"],
    package_data={"tailwind": [tailwind._RELATIVE_TAIWIND_BIN]},
    cmdclass={"bdist_wheel": custom_bdist_wheel},
)
