import click
from migro.migrations import MigrationRepository, DEFAULT_MIGRATION_DIRECTORY


@click.group()
def cli():
    """Data Warehouse migrations"""


@click.command()
@click.option(
    "--pretend",
    is_flag=True,
    default=False,
    help="Show the queries that migro would run",
)
@click.option("--limit", type=int, help="Limit the number of migrations to run")
@click.option("--profile", help="dbt profile key in profiles.yml")
@click.option(
    "--directory",
    help="Directory to store migrations",
    default=DEFAULT_MIGRATION_DIRECTORY,
)
@click.option("--target", help="dbt output target (warehouse) key in profiles.yml")
def up(pretend, limit, profile, directory, target):
    """Run the unapplied SQL in the migrations directory"""

    applied = 0
    migrations_repo = MigrationRepository(
        profile=profile, directory=directory, target=target
    )

    migrations_repo.create_migrations_table()

    for migration in migrations_repo.all():
        if limit and applied >= limit:
            break

        if migration.applied_at:
            continue

        click.echo(click.style(f"Migrating: {migration.file_path}", fg="yellow"))

        if not pretend:
            sql = migrations_repo.apply(migration)
            click.echo(f"— {sql}")
            click.echo(click.style(f"Migrated:  {migration.file_path}", fg="green"))

        applied += 1


@click.command()
@click.argument("name")
@click.option(
    "--directory",
    help="Directory to store migrations",
    default=DEFAULT_MIGRATION_DIRECTORY,
)
def make(name, directory):
    """Create a new migration file. For example, migro make add_user_tharvey"""

    migrations_repo = MigrationRepository(profile=None, directory=directory)
    migration_file = migrations_repo.make(name)

    click.echo(click.style(f"Created: {migration_file}", fg="green"))


cli.add_command(up)
cli.add_command(make)
