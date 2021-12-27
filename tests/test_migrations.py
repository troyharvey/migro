from migro import migrations
import os
import re
import glob
import pytest

PASSWORD_REGEX = "[A-Za-z0-9$%@]{32}"


class TestMigrationRepository:
    def setup_class(self):
        try:
            os.remove("./tests/demo.db")
        except Exception:
            pass

        for f in glob.glob(os.path.join(migrations.MIGRATION_FILE_PATH, "*.sql")):
            os.remove(f)

    def teardown_class(self):
        try:
            os.remove("./tests/demo.db")
        except Exception:
            pass

        for f in glob.glob(os.path.join(migrations.MIGRATION_FILE_PATH, "*.sql")):
            os.remove(f)

    def test_migrations_flow(self):
        migrations_repo = migrations.MigrationRepository("sqlite_profile")

        # Test setting up migrations log table
        migrations_repo.create_migrations_table()
        assert [] == migrations_repo.all()

        # Test making a migration file
        migration_file = migrations_repo.make("create_attribution_table")

        # Add SQL statement to migration file
        with open(migration_file, "w") as f:
            f.write("CREATE TABLE attribution(foo INT);")

        # Does the migration show up in the file listing?
        for f in migrations_repo._get_migration_files():
            assert f.endswith("_create_attribution_table.sql")

        # Test applying the migration
        for m in migrations_repo.all():
            assert m.file_path.endswith("_create_attribution_table.sql")
            migrations_repo.apply(m)

        # There should be no migration left to apply
        for m in migrations_repo.all():
            assert m.applied_at is not None

        # Force migrations file system out of sync with migrations table
        os.rename(migration_file, f"{migrations.MIGRATION_FILE_PATH}/foo.sql")
        with pytest.raises(
            Exception,
            match="Migrations table out of sync with migrations on the filesystem.",
        ):
            migrations_repo.all()


class TestMigration:
    def setup_method(self):
        with open(f"{migrations.MIGRATION_FILE_PATH}/test.sql", "w") as f:
            f.write("select '{{password}}' as pw;")

    def teardown_method(self):
        try:
            os.remove(f"{migrations.MIGRATION_FILE_PATH}/test.sql")
        except Exception:
            pass

    def test_migrations_path_constant(self):
        assert migrations.MIGRATION_FILE_PATH == "./migrations"

    def test_password(self):
        m = migrations.Migration()
        password = m._password()
        assert len(password) == 32
        assert re.match(PASSWORD_REGEX, password)

    def test_sql(self):
        m = migrations.Migration()
        m.file_path = "test.sql"
        assert re.match(f"^select '{PASSWORD_REGEX}' as pw;$", m.sql())
