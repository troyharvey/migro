from migro import database
from unittest import mock

def test_get_sqlite_database_instance():
    db = database.get_database_instance('sqlite_profile')
    assert isinstance(db, database.SqliteDatabase)

def test_get_redshift_database_instance():
    db = database.get_database_instance('redshift_profile')
    assert isinstance(db, database.RedshiftDatabase)

@mock.patch("psycopg2.connect")
def test_redshift_database(psycopg2_mock):
    db = database.RedshiftDatabase(
        host='localhost',
        user='user',
        password='password',
        port=5439,
        dbname='migro',
    )

    db.create_migrations_table()
    db.get_migrations()

    psycopg2_mock.assert_called()
