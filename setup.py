from pathlib import Path
from setuptools import find_packages, setup


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='migro',
    version='0.3.0',
    description='Data Warehouse migrations for dbt.',
    author='Troy Harvey',
    author_email='troyharvey@gmail.com',
    url='https://github.com/troyharvey/migro',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'Jinja2',
        'psycopg2',
        'pyyaml',
        'snowflake-connector-python',
        'sqlparse',
    ],
    extras_require={
        'dev': [
            'black',
            'pytest',
            'pytest-cov',
            'twine',
        ]
    },
    entry_points={
        'console_scripts': [
            'migro = migro.main:cli',
        ],
    },
)
