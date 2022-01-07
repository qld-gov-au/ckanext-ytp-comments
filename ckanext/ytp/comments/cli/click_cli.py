# encoding: utf-8

import click

from ckanext.ytp.comments.cli import command

# Click commands for CKAN 2.9 and above


@click.group()
def comments():
    """ YTP Comments commands
    """
    pass


@comments.command()
def initdb():
    command.initdb()


# explicitly specify name to avoid automagical conversion to dashes
@comments.command(name="init_notifications_db")
def init_notifications_db():
    command.init_notifications_db()


@comments.command()
def updatedb():
    command.updatedb()


def get_commands():
    return [comments]
