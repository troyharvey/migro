import os
import random
import sqlparse
import string

from datetime import datetime
from dataclasses import dataclass

from migro import jinja, database

DEFAULT_MIGRATION_DIRECTORY = "migrations"


@dataclass
class Migration:
    id: int = None
    name: str = None
    applied_at: datetime = None
    directory: str = DEFAULT_MIGRATION_DIRECTORY
    file_path: str = None

    def _password(self):
        """
        Generate a random password with lowercase, uppercase, numbers,
        and special characters
        """
        return "".join(
            random.choice(string.ascii_letters + string.digits + "$%@")
            for _ in range(32)
        )

    def _full_path(self):
        return f"./{self.directory}/{self.file_path}"

    def sql(self):
        sql = jinja.render_jinja_template(self._full_path(), password=self._password())
        return sqlparse.format(sql, strip_comments=True).strip()


class MigrationRepository:
    def __init__(
        self, profile=None, directory=DEFAULT_MIGRATION_DIRECTORY, target=None
    ):
        self.directory = directory
        self.profile = profile
        self.target = target
        self.db = None

    def _get_db(self):
        """
        A singletown database instance for the repository.
        """
        if not self.db:
            self.db = database.get_database_instance(
                profile=self.profile, target=self.target
            )
        return self.db

    def _get_migration_files(self):
        migration_files = []
        for file in sorted(os.listdir(f"./{self.directory}")):
            if file.endswith(".sql"):
                migration_files.append(file)
        return migration_files

    def _log_migration(self, migration: Migration):
        self._get_db().execute(
            f"insert into migrations (migration) values ('{migration.file_path}')"
        )

    def all(self):
        migrations = []
        migration_files = self._get_migration_files()
        migration_records = self._get_db().get_migrations()

        while migration_files:
            migration_file = migration_files.pop(0)
            migration = Migration(file_path=migration_file, directory=self.directory)

            if migration_records:
                migration_record = migration_records.pop(0)

                if migration_record["migration"] not in migration.file_path:
                    raise Exception(
                        (
                            f"""
                            Migrations table out of sync with migrations on the filesystem.
                            {migration.file_path} != {migration_record['migration']}
                            """
                        )
                    )

                migration.id = migration_record["id"]
                migration.name = migration_record["migration"]
                migration.applied_at = migration_record["applied_at"]

            migrations.append(migration)
        return migrations

    def apply(self, migration: Migration) -> str:
        sql = migration.sql()
        if sql:
            self._get_db().execute(sql)
        self._log_migration(migration)
        return sql

    def create_migrations_table(self):
        self._get_db().create_migrations_table()

    def make(self, name) -> str:
        migration_date = datetime.now().strftime("%Y%m%d%H%M%S")
        migration_file = f"./{self.directory}/{migration_date}_{name}.sql"

        if not os.path.exists(migration_file):
            with open(migration_file, "w"):
                pass

        return migration_file
