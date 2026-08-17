# encoding: utf-8

import logging

from sqlalchemy import text

from ckan import model


log = logging.getLogger(__name__)


def initdb():
    """
    Initialises the database with the required tables
    Connects to the CKAN database and creates the comment
    and thread tables ready for use.
    """
    log.info("starting command")

    import ckanext.ytp.comments.model as cmodel
    log.info("Initializing tables")
    cmodel.init_tables()
    log.info("DB tables are setup")


def init_notifications_db():
    """Initialise the comment extension's notifications database tables
    """

    from ckanext.ytp.comments import notification_models
    notification_models.init_tables()
    log.debug("Comment notification preference DB table is setup")


def updatedb():
    """
    Updates the database tables
    """
    log.info("YTP-Comments-UpdateDBCommand: Starting command")

    comment_table = model.meta.metadata.tables.get('comment')
    if comment_table:
        if 'deleted_by_user_id' not in comment_table.columns:
            log.info("YTP-Comments-UpdateDBCommand: 'deleted_by_user_id' field does not exist, adding...")
            with model.meta.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "comment" ADD COLUMN "deleted_by_user_id" text NULL'))

        if not any(x for x in comment_table.foreign_key_constraints if x.name == 'comment_user_deleted_by_user_id_fkey'):
            log.info("YTP-Comments-UpdateDBCommand: 'comment_user_deleted_by_user_id_fkey' foreign_key does not exist, adding...")
            with model.meta.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "comment" ADD CONSTRAINT "comment_user_deleted_by_user_id_fkey" FOREIGN KEY ("deleted_by_user_id") REFERENCES "user" ("id")'))
