#!/usr/bin/env python
from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="matrix-bot",
    version="0.0.6",
    description="A bot for Matrix",
    long_description=read('README.rst'),
    author=["Kegan Dougal", "Pavel Kardash"],
    author_email=["kegsay@gmail.com", "slipeer@gmail.com"],
    url="https://github.com/Slipeer/Matrix-NEB",
    packages=['matrix_bot', 'matrix_bot/mbot', 'matrix_bot/plugins'],
    license="APACHE",
    install_requires=[
        "matrix_client",
        "Flask",
        "python-dateutil",
        "langdetect"
    ],
    dependency_links=[
        "https://github.com/matrix-org/matrix-python-sdk/tarball/v0.0.6#egg=matrix_client-0.0.6"
    ],
    entry_points={
        'console_scripts': ['matrix-bot = matrix_bot.bot:main']
    },
    data_files=[
        ("", ["LICENSE"]),
        # ("/lib/systemd/system/", ["contrib/systemd/matrix-bot.service"]),
    ],
)
