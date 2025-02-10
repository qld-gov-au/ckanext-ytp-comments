import datetime

from sqlalchemy import Column, Table, types
from sqlalchemy.ext.declarative import declarative_base

from ckan.model import meta
from ckan.model.types import make_uuid

log = __import__('logging').getLogger(__name__)

Base = declarative_base(metadata=meta.metadata)

comment_notification_recipient_table = Table('comment_notification_recipient', meta.metadata,
                                             Column('id', types.UnicodeText, primary_key=True,
                                                    default=make_uuid),
                                             Column('timestamp', types.DateTime, default=datetime.datetime.utcnow),
                                             Column('user_id', types.UnicodeText),
                                             Column('thread_id', types.UnicodeText),
                                             Column('comment_id', types.UnicodeText, default=u''),
                                             Column('notification_level', types.UnicodeText),
                                             Column('action', types.UnicodeText)
                                             )


class CommentNotificationRecipient(Base):

    __table__ = comment_notification_recipient_table

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.timestamp = datetime.datetime.utcnow()


def init_tables():
    meta.metadata.create_all(meta.engine)
