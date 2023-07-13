# encoding: utf-8

import os
import six

import pytest
import factory
from werkzeug.datastructures import FileStorage as MockFileStorage

from ckan.lib import uploader
from ckan.tests import factories, helpers

from ckanext.ytp.comments import model as ytp_model


@pytest.fixture
def dataset():
    return factories.Dataset(owner_org=factories.Organization()['id'])


@pytest.fixture
def resource():
    return factories.Resource()


class Comment(factory.Factory):
    """A factory class for creating ytp comment. It must accept user_id and
    package_name, because I don't want to create extra entities in database
    during tests"""

    FACTORY_FOR = ytp_model.Comment

    class Meta:
        model = ytp_model.Comment

    user_id = None
    entity_type = "dataset"
    entity_name = None

    subject = "comment-subject"
    comment = "comment-text"

    @classmethod
    def _build(cls, target_class, *args, **kwargs):
        raise NotImplementedError(".build() isn't supported in CKAN")

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."

        kwargs["url"] = "/{}/{}".format(kwargs["entity_type"], kwargs["entity_name"])

        return helpers.call_action(
            "comment_create", context={"user": kwargs["user_id"], "ignore_auth": True}, **kwargs
        )


@pytest.fixture
def comment_factory():
    return Comment


def _get_test_file():
    file_path = os.path.join(os.path.dirname(__file__), 'data/test.csv')

    with open(file_path) as file:
        test_file = six.BytesIO()
        test_file.write(six.ensure_binary(file.read()))
        test_file.seek(0)

        return MockFileStorage(test_file, "test.csv")


@pytest.fixture
def sysadmin():
    return factories.Sysadmin()


@pytest.fixture
def user():
    return factories.User()


@pytest.fixture
def mock_storage(monkeypatch, ckan_config, tmpdir):
    monkeypatch.setitem(ckan_config, u'ckan.storage_path', str(tmpdir))
    monkeypatch.setattr(uploader, u'get_storage_path', lambda: str(tmpdir))
