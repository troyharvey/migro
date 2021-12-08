import click
from migro.migrations import MigrationRepository


@click.group()
def cli():
    pass

@click.option('--profile')
@click.option('--dry-run', default=False)
@click.command()
def up(profile, dry_run):
    migrations_repo = MigrationRepository(profile)

    if migrations_repo.create_migrations_table():
        click.echo(click.style('Created migrations table.', fg='green'))

    for migration in migrations_repo.all():

        if migration.applied_at:
            continue

        sql = migration.sql()

        click.echo(click.style(f"Migrating: {migration.file_path}", fg='yellow'))
        click.echo(f"— {sql}")

        if not dry_run:
            migrations_repo.apply(migration)
            click.echo(click.style(f"Migrated:  {migration.file_path}", fg='green'))


@click.command()
@click.argument('name')
def make(name):
    migrations_repo = MigrationRepository()
    migration_file = migrations_repo.make(name)

    click.echo(click.style(f"Created: {migration_file}", fg='green'))

cli.add_command(up)
cli.add_command(make)
