import pytest
from migro import database
from unittest import mock


def test_get_sqlite_database_instance():
    db = database.get_database_instance("sqlite_profile")
    assert isinstance(db, database.SqliteDatabase)


def test_get_redshift_database_instance():
    db = database.get_database_instance("redshift_profile")
    assert isinstance(db, database.RedshiftDatabase)


def test_database_not_implemented_errors():
    db = database.Database()

    with pytest.raises(NotImplementedError):
        db._get_connection()

    with pytest.raises(NotImplementedError):
        db.create_migrations_table()

    with pytest.raises(NotImplementedError):
        db.get_migrations()


@mock.patch("psycopg2.connect")
def test_redshift_database(psycopg2_mock):
    db = database.RedshiftDatabase(
        host="localhost",
        user="user",
        password="password",
        port=5439,
        dbname="migro",
    )

    db.create_migrations_table()
    db.get_migrations()

    psycopg2_mock.assert_called()
