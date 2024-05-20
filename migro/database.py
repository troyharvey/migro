import base64
import psycopg2
import psycopg2.extras
import snowflake.connector
import sqlite3
from dataclasses import dataclass
from typing import ClassVar, Optional
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from migro import dbt


def get_database_instance(profile=None, target=None):
    db_config = dbt.get_target_output(profile_name=profile, target=target)

    if db_config["type"] == "redshift":
        return RedshiftDatabase(
            host=db_config["host"],
            user=db_config["user"],
            password=(
                db_config["password"] if "password" in db_config else db_config["pass"]
            ),
            port=db_config["port"],
            dbname=db_config["dbname"],
        )

    if db_config["type"] == "sqlite":
        return SqliteDatabase()

    if db_config["type"] == "snowflake":
        return SnowflakeDatabase(
            account=db_config["account"],
            user=db_config["user"],
            password=db_config.get("password"),
            database=db_config["database"],
            warehouse=db_config["warehouse"],
            private_key=db_config.get("private_key"),
            private_key_passphrase=db_config.get("private_key_passphrase"),
        )


@dataclass
class Database:
    MIGRATIONS_TABLE_SQL: ClassVar[str]

    def _get_connection(self):
        raise NotImplementedError

    def create_migrations_table(self):
        raise NotImplementedError

    def execute(self, sql):
        con = self._get_connection()
        cursor = con.cursor()
        cursor.execute(sql)
        con.commit()
        con.close()

    def get_migrations(self):
        raise NotImplementedError


@dataclass
class SqliteDatabase(Database):
    MIGRATIONS_TABLE_SQL: ClassVar[str] = """
        create table if not exists migrations
        (
            id integer primary key,
            migration varchar(2000) not null,
            applied_at timestamp default current_timestamp not null
        )
    """

    def _get_connection(self):
        return sqlite3.connect("./tests/demo.db")

    def create_migrations_table(self) -> bool:
        self.execute(self.MIGRATIONS_TABLE_SQL)

    def get_migrations(self):
        con = self._get_connection()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM migrations ORDER BY migration ASC")
        migrations = cur.fetchall()
        cur.close()
        con.close()
        return [dict(migration) for migration in migrations]


@dataclass
class RedshiftDatabase(Database):
    host: str
    user: str
    password: str
    port: int
    dbname: str

    MIGRATIONS_TABLE_SQL: ClassVar[str] = """
        create table if not exists migrations
        (
            id int identity not null,
            migration varchar(2000) not null,
            applied_at timestamp default getdate() not null
        )
    """

    def _get_connection(self):
        connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            cursor_factory=psycopg2.extras.DictCursor,
        )
        connection.autocommit = True
        return connection

    def create_migrations_table(self):
        self.execute(self.MIGRATIONS_TABLE_SQL)

    def get_migrations(self):
        con = self._get_connection()
        with con.cursor() as cur:
            cur.execute(
                (
                    """
                SELECT id, migration, applied_at
                FROM public.migrations ORDER BY migration ASC
                """
                )
            )
            migrations = cur.fetchall()
            cur.close()
        con.close()
        return migrations


@dataclass
class SnowflakeDatabase(Database):
    account: str
    user: str
    password: str
    database: str
    warehouse: str
    private_key: Optional[str] = None
    private_key_passphrase: Optional[str] = None

    MIGRATIONS_TABLE_SQL: ClassVar[str] = """
        create table if not exists PUBLIC.migrations
        (
            id int identity not null,
            migration varchar(2000) not null,
            applied_at timestamp default current_timestamp() not null
        )
    """

    def _get_connection(self):
        return snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            database=self.database,
            warehouse=self.warehouse,
            private_key=self._get_private_key(),
        )

    def _get_private_key(self):
        """
        base64 decode the private key, decrypt it, and return an instance of AuthByKeyPair
        See dbt-snowflake private key code:
        https://github.com/dbt-labs/dbt-snowflake/blob/87a6e808dfb025df1eeef3741ad3822635249889/dbt/adapters/snowflake/connections.py#L244
        """
        if not self.private_key:
            return None

        if self.private_key_passphrase:
            encoded_passphrase = self.private_key_passphrase.encode()
        else:
            encoded_passphrase = None

        if self.private_key.startswith("-"):
            p_key = serialization.load_pem_private_key(
                data=bytes(self.private_key, "utf-8"),
                password=encoded_passphrase,
                backend=default_backend(),
            )
        else:
            p_key = serialization.load_der_private_key(
                data=base64.b64decode(self.private_key),
                password=encoded_passphrase,
                backend=default_backend(),
            )

        return p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def create_migrations_table(self):
        self.execute(self.MIGRATIONS_TABLE_SQL)

    def get_migrations(self):
        con = self._get_connection()
        with con.cursor(snowflake.connector.DictCursor) as cur:
            cur.execute(
                (
                    """
                    SELECT ID as "id", MIGRATION as "migration", APPLIED_AT as "applied_at"
                    FROM PUBLIC.migrations ORDER BY migration ASC
                    """
                )
            )
            migrations = cur.fetchall()
            cur.close()
        con.close()
        return migrations
