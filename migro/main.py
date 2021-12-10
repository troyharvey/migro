import click
from migro.migrations import MigrationRepository


@click.group()
def cli():
    """Data Warehouse migrations"""
    pass


@click.option('--pretend/--no-pretend', default=False, help='Show the queries that migro would run')
@click.option('--limit', type=int, help='Limit the number of migrations to run')
@click.option('--dbt-profile', help='dbt profile key in profiles.yml')
@click.command()
def up(pretend, limit, dbt_profile):
    """Run the unapplied SQL in the migrations directory"""

    applied = 0
    migrations_repo = MigrationRepository(dbt_profile)

    migrations_repo.create_migrations_table()

    for migration in migrations_repo.all():

        if limit and applied >= limit:
            break

        if migration.applied_at:
            continue

        click.echo(click.style(f"Migrating: {migration.file_path}", fg='yellow'))

        sql = migration.sql()
        click.echo(f"— {sql}")

        if not pretend:
            migrations_repo.apply(migration)
            click.echo(click.style(f"Migrated:  {migration.file_path}", fg='green'))

        applied += 1


@click.command()
@click.argument('name')
def make(name):
    """Create a new migration file. For example, migro make add_user_tharvey"""

    migrations_repo = MigrationRepository()
    migration_file = migrations_repo.make(name)

    click.echo(click.style(f"Created: {migration_file}", fg='green'))

cli.add_command(up)
cli.add_command(make)
