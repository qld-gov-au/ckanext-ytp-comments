# encoding: utf-8

from ckan import model
from ckan.lib.cli import CkanCommand

from ckanext.ytp.comments.cli.command import initdb, init_notifications_db, updatedb


class InitDBCommand(CkanCommand):
    """
    Initialises the database with the required tables
    Connects to the CKAN database and creates the comment
    and thread tables ready for use.
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def __init__(self, name):
        super(InitDBCommand, self).__init__(name)

    def command(self):
        self._load_config()
        initdb()


class InitNotificationsDB(CkanCommand):
    """Initialise the comment extension's notifications database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()
        init_notifications_db()


class UpdateDBCommand(CkanCommand):
    """
    Updates the database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def __init__(self, name):
        super(UpdateDBCommand, self).__init__(name)

    def command(self):
        self._load_config()
        updatedb()


class CommentsDBCommand(CkanCommand):
    """
    Run commands to set up the Comments database.

    The available commands are:

        initdb - Initialize the database tables for this extension

        init_notifications_db - Initialise database tables for notifying users
                                of comments relevant to them

        updatedb - Add columns to existing tables to store deletion metadata
     """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def __init__(self, name):
        super(CommentsDBCommand, self).__init__(name)

    def command(self):
        self._load_config()
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        cmd = self.args[0]
        if cmd == 'initdb':
            initdb()
        elif cmd == 'init_notifications_db':
            init_notifications_db()
        elif cmd == 'updatedb':
            updatedb()
        else:
            self.parser.error('Command not recognized: %r', cmd)
