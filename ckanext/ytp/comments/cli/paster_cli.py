# encoding: utf-8

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
