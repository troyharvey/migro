from migro.migrations import MigrationRepository
import os


class TestMigrations:
    def setup_method(self):
        try:
            os.remove("./tests/demo.db")
        except:
            pass

    def teardown_method(self):
        os.remove("./tests/demo.db")

    def test_get_migration_files(self):
        migrations = MigrationRepository()
        migration_files = migrations._get_migration_files()
        assert migration_files == []

    def test_all(self):
        migrations = MigrationRepository('sqlite_profile')
        migrations = migrations.all()
        assert migrations == []
