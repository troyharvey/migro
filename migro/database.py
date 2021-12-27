import psycopg2
import psycopg2.extras
import sqlite3
from dataclasses import dataclass
from typing import ClassVar

from migro import dbt


def get_database_instance(profile=None):
    db_config = dbt.get_output(profile=profile)

    if db_config["type"] == "redshift":
        return RedshiftDatabase(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"]
            if "password" in db_config
            else db_config["pass"],
            port=db_config["port"],
            dbname=db_config["dbname"],
        )

    if db_config["type"] == "sqlite":
        return SqliteDatabase()


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

    MIGRATIONS_TABLE_SQL: ClassVar[
        str
    ] = """
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

    MIGRATIONS_TABLE_SQL: ClassVar[
        str
    ] = """
        create table if not exists migrations
        (
            id int identity not null,
            migration varchar(2000) not null,
            applied_at timestamp default getdate() not null
        )
    """

    def _get_connection(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            cursor_factory=psycopg2.extras.DictCursor,
        )

    def create_migrations_table(self):
        self.execute(self.MIGRATIONS_TABLE_SQL)

    def get_migrations(self):
        con = self._get_connection()
        with con.cursor() as cur:
            cur.execute((
                """
                SELECT id, migration, applied_at
                FROM public.migrations ORDER BY migration ASC
                """
            ))
            migrations = cur.fetchall()
            cur.close()
        con.close()
        return migrations
