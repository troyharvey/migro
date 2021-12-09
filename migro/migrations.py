import os
import random
import string

from datetime import datetime
from dataclasses import dataclass

from migro import jinja, database

MIGRATION_FILE_PATH = './migrations'


def generate_password():
    """
    Generate a random password with lowercase, uppercase, numbers and special characters
    """
    return ''.join(random.choice(string.ascii_letters + string.digits + '$%@') for _ in range(32))


@dataclass
class Migration:
    id: int = None
    name: str = None
    applied_at: datetime = None
    file_path: str = None

    def sql(self):
        sql = jinja.render_jinja_template(
            f"{MIGRATION_FILE_PATH}/{self.file_path}",
            password=generate_password()
        )
        return sql.strip()


class MigrationRepository:

    def __init__(self, profile=None):
        self.profile = profile
        self.db = database.get_database_instance(profile)

    def _get_migration_files(self):
        migration_files = []
        for file in sorted(os.listdir(MIGRATION_FILE_PATH)):
            if file.endswith('.sql'):
                migration_files.append(file)
        return migration_files

    def _log_migration(self, migration:Migration):
        self.db.execute(f"insert into migrations (migration) values ('{migration.file_path}')")

    def all(self):
        migrations = []
        migration_files = self._get_migration_files()
        migration_records = self.db.get_migrations()

        while migration_files:
            migration = Migration(
                file_path = migration_files.pop(0)
            )

            if migration_records:
                migration_record = migration_records.pop(0)

                if migration.file_path != migration_record['migration']:
                    raise Exception(f'Migrations table out of sync with migrations on the filesystem. {migration.file_path} != {migration.name}')

                migration.id = migration_record['id']
                migration.name = migration_record['migration']
                migration.applied_at = migration_record['applied_at']

            migrations.append(migration)
        return migrations

    def apply(self, migration:Migration):
        sql = migration.sql()
        if sql:
            self.db.execute(sql)
        self._log_migration(migration)

    def create_migrations_table(self) -> bool:
        self.db.create_migrations_table()


    def make(self, name) -> str:
        migration_date = datetime.now().strftime('%Y%m%d%H%M%S')
        migration_file = f"{MIGRATION_FILE_PATH}/{migration_date}_{name}.sql"

        if not os.path.exists(migration_file):
            with open(migration_file, 'w'): pass

        return migration_file
