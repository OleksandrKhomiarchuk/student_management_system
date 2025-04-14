import click
from click import command
from flask.cli import with_appcontext
from database.models import db
from scripts.generate_data import generate_data

@click.command("init-db")
@with_appcontext
def init_db_command() -> command(): # pragma: no cover
    """
    Clear the existing data and create new tables.
    """
    db.drop_all()
    db.create_all()
    click.echo('Database initialized.')

@click.command("generate-data")
@with_appcontext
def generate_data_command() -> command(): # pragma: no cover
    """
    Fills in the initial fake data
    """
    generate_data()
    click.echo('Fake data generated.')
