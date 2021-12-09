from setuptools import find_packages, setup

setup(
    name='migro',
    version='0.0.2',
    description='Redshift Data Warehouse migrations for dbt.',
    author='Troy Harvey',
    author_email='troyharvey@gmail.com',
    license='MIT',
    url='https://github.com/troyharvey/migro',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'Jinja2',
        'psycopg2',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'migro = migro.main:cli',
        ],
    },
)
