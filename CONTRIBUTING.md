# Contributing to migro

1. Install Python dependencies.

        pip install --editable .['dev']

1. Build a distribution wheel.

        python setup.py bdist_wheel

1. Install the wheel in a dbt project and test the changes.

        pip install ~/Projects/migro/dist/migro-0.0.4-py3-none-any.whl --force-reinstall

## Tagging a Release

1. Add a [pypi.org API token](https://packaging.python.org/en/latest/specifications/pypirc/#using-a-pypi-token) to `/.pypirc`
1. Bump the version number in `setup.py`
1. Build a distribution wheel.

        python setup.py bdist_wheel

1. Upload the new version.

        twine upload dist/*
