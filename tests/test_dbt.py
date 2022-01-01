import pytest

from migro import dbt
from pathlib import Path


def test_get_output():
    output = dbt.get_output()
    assert output["type"] == "redshift"
    assert output["host"] == "localhost"
    assert output["user"] == "tharvey"
    assert output["port"] == 55091
    assert output["dbname"] == "sandbox_tharvey"


def test_get_output_sqlite():
    output = dbt.get_output(profile="sqlite_profile")
    assert output["type"] == "sqlite"


def test_get_output_without_dbt_profile_yaml():
    Path("./profiles.yml").rename("./profiles.yml.bak")
    with pytest.raises(SystemExit):
        dbt.get_output()
    Path("./profiles.yml.bak").rename("./profiles.yml")
