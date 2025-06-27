# setup.py

from setuptools import setup

APP = ['mov_converter.py']
OPTIONS = {
    "argv_emulation": False,  # отключаем, он вызывает Carbon
    "includes": ["tkinter"],
    "packages": [],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
