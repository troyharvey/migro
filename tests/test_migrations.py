from migro import migrations
import os
import re
import glob

PASSWORD_REGEX = "[A-Za-z0-9$%@]{32}"


class TestMigrationRepository:
    def setup_class(self):
        try:
            os.remove("./tests/demo.db")
        except:
            pass

        for f in glob.glob(os.path.join(migrations.MIGRATION_FILE_PATH, "*.sql")):
            os.remove(f)

    def teardown_class(self):
        try:
            os.remove("./tests/demo.db")
        except:
            pass

        for f in glob.glob(os.path.join(migrations.MIGRATION_FILE_PATH, "*.sql")):
            os.remove(f)

    def test_migrations_flow(self):
        migrations_repo = migrations.MigrationRepository("sqlite_profile")

        # Test setting up migrations log table
        migrations_repo.create_migrations_table()
        assert [] == migrations_repo.all()

        # Test making a migration file
        migrations_repo.make("create_jdoe_user")

        # Does jdoe migration show up in the file listing?
        for f in migrations_repo._get_migration_files():
            assert f.endswith("_create_jdoe_user.sql")

        for m in migrations_repo.all():
            assert m.file_path.endswith("_create_jdoe_user.sql")
            migrations_repo.apply(m)

        for m in migrations_repo.all():
            assert m.applied_at is not None


class TestMigration:
    def setup_method(self):
        with open(f"{migrations.MIGRATION_FILE_PATH}/test.sql", "w") as f:
            f.write("select '{{password}}' as pw;")

    def teardown_method(self):
        try:
            os.remove(f"{migrations.MIGRATION_FILE_PATH}/test.sql")
        except:
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
