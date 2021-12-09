from migro import dbt


def test_output():
    output = dbt.get_output()
    assert output['type'] == 'redshift'
    assert output['host'] == 'localhost'
    assert output['user'] == 'tharvey'
    assert output['port'] == 55091
    assert output['dbname'] == 'sandbox_tharvey'

def test_output_sqlite():
    output = dbt.get_output(profile='sqlite_profile')
    assert output['type'] == 'sqlite'
