#!/usr/bin/env python
from setuptools import setup, find_packages
import os


def datadir(data):
    return [(d, [os.path.join(d,f) for f in files])
        for d, folders, files in os.walk(data)]



def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def molist():
    """Generate list to locales include."""
    res = []
    langs = [lang for lang in os.listdir('locale') if os.path.isdir(lang)]
    for lang in langs:
        path = os.path.join('locale', lang, 'LC_MESSAGES')
        dpath = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
        files = [
            os.path.join(path, fil)
            for fil in os.listdir(path)
            if fil.endswith(('.mo', '.pot'))
        ]
        res.append(
            (dpath, files)
        )
    return res

def filelist(folder):
    """Generate files list."""
    res = []
    langs = [
        lang
        for lang in os.listdir(os.path.join('matrix_bot', folder))
        if os.path.isdir(os.path.join('matrix_bot', folder, lang))
    ]
    for lang in langs:
        path = os.path.join(folder, lang, 'LC_MESSAGES')
        files = [
            os.path.join(path, fil)
            for fil in os.listdir(os.path.join('matrix_bot', path))
            if fil.endswith(('.mo', '.pot', 'README'))
        ]
        res = res+files
    return res

print filelist('locale')

setup(
    name="matrix-bot",
    version="0.0.6",
    description="A bot for Matrix",
    long_description=read('README.rst'),
    author=["Kegan Dougal", "Pavel Kardash"],
    author_email=["kegsay@gmail.com", "slipeer@gmail.com"],
    url="https://github.com/Slipeer/Matrix-NEB",
    include_package_data=True,
    packages=find_packages(),
    package_data={'matrix_bot': filelist('locale')},
    license="APACHE",
    install_requires=[
        "matrix_client",
        "Flask",
        "python-dateutil",
        "langdetect",
        "polib"
    ],
    dependency_links=[
        "https://github.com/matrix-org/matrix-python-sdk/tarball/v0.0.6#egg=matrix_client-0.0.6"
    ],
    entry_points={
        'console_scripts': ['matrix-bot = matrix_bot.bot:main']
    }
)
