# Contributing to migro

1. Install Python dependencies.

        pip install --editable '.[dev]'

1. Run migro

        migro --help

## Test in a dbt Project

1. Install `migro` in edit mode inside a dbt project.

        pip install -e ~/Projects/migro

1. Build a distribution wheel.

        python setup.py bdist_wheel

1. Install the wheel in a dbt project and test the changes.

        pip install ~/Projects/migro/dist/migro-0.x.y-py3-none-any.whl --force-reinstall

## Tagging a Release

1. Add a [pypi.org API token](https://packaging.python.org/en/latest/specifications/pypirc/#using-a-pypi-token) to `/.pypirc`
1. Bump the version number in `setup.py`
1. Build a distribution wheel.

        python setup.py bdist_wheel

1. Upload the new version.

        twine upload dist/*

## Upgrading Dependencies

1. Install pip tools

        pip install pip-tools

1. Update the dependencies in pyproject and setup.py.
1. Compile the requirements file.

        pip-compile -o requirements.txt pyproject.toml

1. Compile the dev requirements file.

        pip-compile --extra dev -o dev-requirements.txt pyproject.toml
