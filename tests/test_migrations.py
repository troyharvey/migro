from migro import migrations
import os
import re


class TestMigrations:
    def setup_method(self):
        try:
            os.remove("./tests/demo.db")
        except:
            pass

    def teardown_method(self):
        try:
            os.remove("./tests/demo.db")
        except:
            pass

    def test_migrations_path_constant(self):
        assert migrations.MIGRATION_FILE_PATH == './migrations'

    def test_generate_password(self):
        password = migrations.generate_password()
        assert len(password) == 32
        assert re.match('^[A-Za-z0-9$%@]{32}$', password)



    # def test_get_migration_files(self):
    #     migrations = MigrationRepository()
    #     migration_files = migrations._get_migration_files()
    #     assert migration_files == []

    # def test_all(self):
    #     migrations = MigrationRepository('sqlite_profile')
    #     migrations = migrations.all()
    #     assert migrations == []
