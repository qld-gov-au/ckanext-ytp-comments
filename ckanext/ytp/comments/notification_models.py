import datetime

from sqlalchemy import Table, Column
from sqlalchemy import types
from ckan.model.meta import engine, metadata
from ckan.model.types import make_uuid

log = __import__('logging').getLogger(__name__)


comment_notification_recipient_table = Table('comment_notification_recipient', metadata,
                                             Column('id', types.UnicodeText, primary_key=True,
                                                    default=make_uuid),
                                             Column('timestamp', types.DateTime, default=datetime.datetime.utcnow),
                                             Column('user_id', types.UnicodeText),
                                             Column('thread_id', types.UnicodeText),
                                             Column('comment_id', types.UnicodeText, default=u''),
                                             Column('notification_level', types.UnicodeText),
                                             Column('action', types.UnicodeText)
                                             )


class CommentNotificationRecipient(object):

    __table__ = comment_notification_recipient_table

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = make_uuid()
        self.timestamp = datetime.datetime.utcnow()


def init_tables():
    metadata.create_all(engine)
