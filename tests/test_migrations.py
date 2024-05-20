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

        for f in glob.glob(
            os.path.join("./", migrations.DEFAULT_MIGRATION_DIRECTORY, "*.sql")
        ):
            os.remove(f)

    def teardown_class(self):
        try:
            os.remove("./tests/demo.db")
        except Exception:
            pass

        for f in glob.glob(
            os.path.join("./", migrations.DEFAULT_MIGRATION_DIRECTORY, "*.sql")
        ):
            os.remove(f)

    def test_migrations_flow(self):
        migrations_repo = migrations.MigrationRepository(profile="sqlite_profile")

        # Test setting up migrations log table
        migrations_repo.create_migrations_table()
        assert [] == migrations_repo.all()

        # Test making a migration file
        migration_file = migrations_repo.make("create_attribution_table")

        # Add SQL statement to migration file
        with open(migration_file, "w") as f:
            f.write("CREATE TABLE attribution(foo TEXT);")

        # Does the migration show up in the file listing?
        for f in migrations_repo._get_migration_files():
            assert f.endswith("_create_attribution_table.sql")

        # Test applying the migration
        for m in migrations_repo.all():
            assert m.file_path.endswith("_create_attribution_table.sql")
            sql = migrations_repo.apply(m)
            assert sql == "CREATE TABLE attribution(foo TEXT);"

        # There should be no migration left to apply
        for m in migrations_repo.all():
            assert m.applied_at is not None

        # Force migrations file system out of sync with migrations table
        os.rename(migration_file, f"{migrations.DEFAULT_MIGRATION_DIRECTORY}/foo.sql")
        with pytest.raises(
            Exception,
            match="Migrations table out of sync with migrations on the filesystem.",
        ):
            migrations_repo.all()


class TestMigration:
    DIRECTORY = f"./{migrations.DEFAULT_MIGRATION_DIRECTORY}"

    def setup_method(self):
        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

        with open(f"{self.DIRECTORY}/test.sql", "w") as f:
            f.write(
                """
                -- This comment should be removed when sql is rendered
                select '{{password}}' as pw;
                """
            )

    def teardown_method(self):
        for f in glob.glob(
            os.path.join("./", migrations.DEFAULT_MIGRATION_DIRECTORY, "*.sql")
        ):
            os.remove(f)

    def test_migrations_path_constant(self):
        assert migrations.DEFAULT_MIGRATION_DIRECTORY == "migrations"

    def test_password(self):
        m = migrations.Migration()
        password = m._password()
        assert len(password) == 32
        assert re.match(PASSWORD_REGEX, password)

    def test_sql(self):
        m = migrations.Migration(file_path="test.sql")
        sql = m.sql()
        assert re.match(f"^select '{PASSWORD_REGEX}' as pw;$", sql)


class TestMigrationWithCustomDirectory:
    DIRECTORY = "./migrations_snowflake"

    def setup_method(self):
        if not os.path.exists(self.DIRECTORY):
            os.makedirs(self.DIRECTORY)

        with open(f"{self.DIRECTORY}/test.sql", "w") as f:
            f.write(
                """
                -- This comment should be removed when sql is rendered
                select '{{password}}' as pw;
                """
            )

    def teardown_method(self):
        for f in glob.glob(os.path.join("./", self.DIRECTORY, "*.sql")):
            os.remove(f)

    def test_sql(self):
        m = migrations.Migration(file_path="test.sql", directory=self.DIRECTORY)
        sql = m.sql()
        assert re.match(f"^select '{PASSWORD_REGEX}' as pw;$", sql)
