import click
from migro.migrations import MigrationRepository


@click.group()
def cli():
    pass


@click.option('--pretend/--no-pretend', default=False)
@click.option('--limit', type=int)
@click.option('--dbt-profile')
@click.command()
def up(pretend, limit, dbt_profile):
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
    migrations_repo = MigrationRepository()
    migration_file = migrations_repo.make(name)

    click.echo(click.style(f"Created: {migration_file}", fg='green'))

cli.add_command(up)
cli.add_command(make)
