# encoding: utf-8

import logging

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

    from sqlalchemy import MetaData, DDL
    meta = MetaData()
    meta.reflect(bind=model.Session.get_bind())

    if 'comment' in meta.tables and 'deleted_by_user_id' not in meta.tables['comment'].columns:
        log.info("YTP-Comments-UpdateDBCommand: 'deleted_by_user_id' field does not exist, adding...")
        DDL('ALTER TABLE "comment" ADD COLUMN "deleted_by_user_id" text NULL').execute(model.Session.get_bind())

    if 'comment' in meta.tables and not any(x for x in meta.tables['comment'].foreign_key_constraints if x.name == 'comment_user_deleted_by_user_id_fkey'):
        log.info("YTP-Comments-UpdateDBCommand: 'comment_user_deleted_by_user_id_fkey' foreign_key does not exist, adding...")
        DDL('ALTER TABLE "comment" ADD CONSTRAINT "comment_user_deleted_by_user_id_fkey" FOREIGN KEY ("deleted_by_user_id") REFERENCES "user" ("id")').execute(model.Session.get_bind())
