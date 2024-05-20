import os
import pytest

from migro import dbt


def test_get_output():
    profile = {
        "outputs": {
            "redshift": {
                "type": "redshift",
                "threads": 8,
                "host": "localhost",
                "port": "5555",
                "user": "tharvey",
                "pass": "password",
                "dbname": "derp",
                "schema": "public",
                "ra3_node": True,
                "retries": 3,
            },
            "snowflake": {
                "type": "snowflake",
                "account": "xt83740.us-east-1",
                "user": "troyharvey",
                "password": "password",
                "database": "US_TESTING",
                "warehouse": "US_TESTING_WH",
                "schema": "PUBLIC",
                "threads": 4,
            },
        },
        "target": "redshift",
    }

    output = dbt._get_output(profile=profile, target="snowflake")
    assert output["type"] == "snowflake"
    assert output["account"] == "xt83740.us-east-1"
    assert output["user"] == "troyharvey"
    assert output["database"] == "US_TESTING"
    assert output["warehouse"] == "US_TESTING_WH"
    assert output["schema"] == "PUBLIC"
    assert output["threads"] == 4

    output = dbt._get_output(profile=profile)
    assert output["type"] == "redshift"
    assert output["host"] == "localhost"
    assert output["port"] == "5555"
    assert output["user"] == "tharvey"
    assert output["dbname"] == "derp"
    assert output["schema"] == "public"


def test_get_output_no_target_specified():
    profile = {
        "outputs": {
            "redshift": {
                "type": "redshift",
                "host": "localhost",
            }
        }
    }

    with pytest.raises(Exception) as e:
        dbt._get_output(profile=profile)
    assert str(e.value) == "No target specified"


def test_get_output_target_not_found():
    profile = {
        "outputs": {
            "redshift": {
                "type": "redshift",
                "host": "localhost",
            }
        }
    }

    with pytest.raises(Exception) as e:
        dbt._get_output(profile=profile, target="donkeykong")
    assert str(e.value) == "Target donkeykong not found in profiles.yml"


def test_get_profile():
    profiles = {
        "default": {
            "outputs": {
                "redshift": {
                    "type": "redshift",
                    "threads": 8,
                    "host": "localhost",
                }
            },
            "target": "redshift",
        },
        "dev": {
            "outputs": {
                "snowflake": {
                    "type": "snowflake",
                }
            },
            "target": "snowflake",
        },
        "config": {"send_anonymous_usage_stats": False},
    }

    profile = dbt._get_profile(profiles, "default")
    assert profile.get("target") == "redshift"

    profile = dbt._get_profile(profiles, "dev")
    assert profile.get("target") == "snowflake"


def test_get_profile_no_profile_name_provided():
    profiles = {
        "default": {
            "outputs": {
                "redshift": {
                    "type": "redshift",
                    "threads": 8,
                    "host": "localhost",
                }
            },
            "target": "redshift",
        },
        "config": {"send_anonymous_usage_stats": False},
    }

    profile = dbt._get_profile(profiles)
    assert profile.get("target") == "redshift"


def test_get_profile_not_found():
    profiles = {
        "default": {
            "outputs": {
                "redshift": {
                    "type": "redshift",
                    "threads": 8,
                    "host": "localhost",
                }
            },
            "target": "redshift",
        },
        "dev": {
            "outputs": {
                "snowflake": {
                    "type": "snowflake",
                }
            },
            "target": "snowflake",
        },
        "config": {"send_anonymous_usage_stats": False},
    }

    profile = dbt._get_profile(profiles, "default")
    assert profile.get("target") == "redshift"

    profile = dbt._get_profile(profiles, "dev")
    assert profile.get("target") == "snowflake"

    with pytest.raises(Exception) as e:
        dbt._get_profile(profiles, "skibiti")
    assert str(e.value) == "Profile skibiti not found in profiles.yml"


def test_profiles_yaml_to_dict():
    profiles_path = "./profiles.yml"
    profiles = dbt._profiles_yaml_to_dict(profiles_path)
    assert profiles["redshift_profile"]["target"] == "dev"
    assert profiles["sqlite_profile"]["outputs"]["dev"]["type"] == "sqlite"


def test_get_profiles_path(monkeypatch):
    def mock_isfile(path):
        if path == "./profiles.yml":
            return True

    monkeypatch.setattr(os.path, "isfile", mock_isfile)

    assert dbt._get_profiles_path() == "./profiles.yml"


def test_get_profiles_path_dbt(monkeypatch):
    def mock_isfile(path):
        if path == "./profiles.yml":
            return False
        elif path == "~/.dbt/profiles.yml":
            return True

    monkeypatch.setattr(os.path, "isfile", mock_isfile)

    assert dbt._get_profiles_path() == "~/.dbt/profiles.yml"


def test_get_profiles_path_exception(monkeypatch):
    def mock_isfile(path):
        return False

    monkeypatch.setattr(os.path, "isfile", mock_isfile)

    with pytest.raises(Exception) as e_info:
        dbt._get_profiles_path()

    assert str(e_info.value) == "Missing dbt profiles.yml"
