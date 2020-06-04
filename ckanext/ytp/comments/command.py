import ckan.model as model
import logging

from ckan.lib.cli import CkanCommand

log = logging.getLogger(__name__)


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
        log.info("starting command")
        self._load_config()

        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import ckanext.ytp.comments.model as cmodel
        log.info("Initializing tables")
        cmodel.init_tables()
        log.info("DB tables are setup")


class InitNotificationsDB(CkanCommand):
    """Initialise the comment extension's notifications database tables
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def command(self):
        self._load_config()

        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import notification_models
        notification_models.init_tables()
        log.debug("Comment notification preference DB table is setup")


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
        print ("YTP-Comments-UpdateDBCommand: Starting command")
        self._load_config()

        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        from sqlalchemy import Column, types, MetaData, DDL
        meta = MetaData(bind=model.Session.get_bind(), reflect=True)

        if 'comment' in meta.tables and 'deleted_by_user_id' not in meta.tables['comment'].columns:
            print("YTP-Comments-UpdateDBCommand: 'deleted_by_user_id' field does not exist, adding...")
            DDL('ALTER TABLE "comment" ADD COLUMN "deleted_by_user_id" text NULL').execute(model.Session.get_bind())

        if 'comment' in meta.tables and not any(x for x in meta.tables['comment'].foreign_key_constraints if x.name == 'comment_user_deleted_by_user_id_fkey'):
            print("YTP-Comments-UpdateDBCommand: 'comment_user_deleted_by_user_id_fkey' foreign_key does not exist, adding...")
            DDL('ALTER TABLE "comment" ADD CONSTRAINT "comment_user_deleted_by_user_id_fkey" FOREIGN KEY ("deleted_by_user_id") REFERENCES "user" ("id")').execute(model.Session.get_bind())
