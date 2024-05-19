import base64
import pytest
from migro import database
from unittest import mock


def test_get_sqlite_database_instance():
    db = database.get_database_instance("sqlite_profile")
    assert isinstance(db, database.SqliteDatabase)


def test_get_redshift_database_instance():
    db = database.get_database_instance("redshift_profile")
    assert isinstance(db, database.RedshiftDatabase)


def test_get_snowflake_database_instance():
    db = database.get_database_instance("snowflake_profile")
    assert isinstance(db, database.SnowflakeDatabase)


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


@mock.patch("snowflake.connector.connect")
def test_snowflake_database(snowflake_mock):
    db = database.SnowflakeDatabase(
        account="account",
        user="user",
        password="password",
        database="database",
        warehouse="warehouse",
    )

    db.create_migrations_table()
    db.get_migrations()

    snowflake_mock.assert_called()


def test_get_private_key_pem():
    """
    openssl command used to create the pem fixture:
    openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out tests/fixtures/private_key.pem
    """
    with open("tests/fixtures/private_key.pem", "r") as f:
        pem_key = f.read()

    db = database.SnowflakeDatabase(
        account="test",
        user="test",
        password="test",
        database="test",
        warehouse="test",
        private_key=pem_key,
        private_key_passphrase="fripper",
    )
    result = db._get_private_key()

    assert isinstance(result, bytes)


def test_get_private_key_pem_no_passphrase():
    """
    openssl command used to create the pem fixture:
    openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out tests/fixtures/private_key_no_passphrase.pem -nocrypt
    """

    with open("tests/fixtures/private_key_no_passphrase.pem", "r") as f:
        pem_key = f.read()

    db = database.SnowflakeDatabase(
        account="test",
        user="test",
        password="test",
        database="test",
        warehouse="test",
        private_key=pem_key,
    )
    result = db._get_private_key()

    assert isinstance(result, bytes)


def test_get_private_key_der():
    """
    openssl command used to create the der fixture:
    openssl pkcs8 -topk8 -in tests/fixtures/private_key.pem -outform DER -out tests/fixtures/private_key.der
    """
    with open("tests/fixtures/private_key.der", "rb") as f:
        der_key = f.read()
        der_key = base64.b64encode(der_key).decode("utf-8")

    db = database.SnowflakeDatabase(
        account="test",
        user="test",
        password="test",
        database="test",
        warehouse="test",
        private_key=der_key,
        private_key_passphrase="fripper",
    )
    result = db._get_private_key()

    assert isinstance(result, bytes)
