from click.testing import CliRunner
from migro import main


def test_cli():
    runner = CliRunner()
    result = runner.invoke(main.cli)
    assert result.exit_code == 0
    assert "Data Warehouse migrations" in result.output


def test_make():
    runner = CliRunner()
    result = runner.invoke(main.make, "add_user_tharvey")
    assert result.exit_code == 0
    assert "Created:" in result.output
    assert "_add_user_tharvey.sql" in result.output

    result = runner.invoke(main.make, "add_user_zharvey")
    assert "Created:" in result.output
    assert "_add_user_zharvey.sql" in result.output


def test_up_pretend():
    runner = CliRunner()
    result = runner.invoke(
        main.up, ["--pretend", "--limit=1", "--dbt-profile=sqlite_profile"]
    )
    assert result.exit_code == 0
    assert "Migrating:" in result.output
    assert "_add_user_tharvey.sql" in result.output


def test_up():
    runner = CliRunner()
    result = runner.invoke(main.up, ["--limit=1", "--dbt-profile=sqlite_profile"])
    assert result.exit_code == 0
    assert "Migrating:" in result.output
    assert "_add_user_tharvey.sql" in result.output
    assert "Migrated:" in result.output

    result = runner.invoke(main.up, ["--dbt-profile=sqlite_profile"])
    assert result.exit_code == 0
    assert "Migrating:" in result.output
    assert "_add_user_zharvey.sql" in result.output
    assert "Migrated:" in result.output
