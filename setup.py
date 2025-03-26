from setuptools import setup

setup(
    name="ai-cli-tool",
    version="0.1",
    py_modules=["main"],
    install_requires=[
        "requests",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "ai=main:main",
        ],
    },
)