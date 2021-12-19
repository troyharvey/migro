from migro import database

def test_get_sqlite_database_instance():
    db = database.get_database_instance('sqlite_profile')
    assert isinstance(db, database.SqliteDatabase)

def test_get_redshift_database_instance():
    db = database.get_database_instance('redshift_profile')
    assert isinstance(db, database.RedshiftDatabase)
