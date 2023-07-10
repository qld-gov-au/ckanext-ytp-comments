# encoding: utf-8

import os
import six
from datetime import datetime as dt

import pytest
import factory
from faker import Faker
from werkzeug.datastructures import FileStorage as MockFileStorage

import ckan.tests.helpers as helpers
from ckan.tests import factories

from ckan.lib import uploader
from ckanext.ytp.comments import model as ytp_model

fake = Faker()


class OrganizationFactory(factories.Organization):
    name = factory.LazyAttribute(
        lambda _: fake.slug() + "" + dt.now().strftime("%Y%m%d-%H%M%S"))


class DatasetFactory(factories.Dataset):
    name = factory.LazyAttribute(
        lambda _: fake.slug() + "" + dt.now().strftime("%Y%m%d-%H%M%S"))
    author_email = factory.LazyAttribute(lambda _: fake.email())
    version = "1.0"
    license_id = "other-open"
    owner_org = factory.LazyAttribute(lambda _: OrganizationFactory()["id"])
    validation_options = ""
    validation_status = ""
    validation_timestamp = ""


@pytest.fixture
def dataset_factory():
    return DatasetFactory


@pytest.fixture
def dataset():
    return DatasetFactory()


class ResourceFactory(factories.Resource):
    id = factory.LazyAttribute(lambda _: fake.uuid4())
    description = factory.LazyAttribute(lambda _: fake.sentence())
    name = factory.LazyAttribute(
        lambda _: fake.slug() + "" + dt.now().strftime("%Y%m%d-%H%M%S"))
    last_modified = factory.LazyAttribute(lambda _: str(dt.now()))

    upload = factory.LazyAttribute(lambda _: _get_test_file())
    format = "CSV"
    url_type = "upload"
    url = None

    package_id = factory.LazyAttribute(lambda _: DatasetFactory()["id"])

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."

        kwargs.setdefault("context", {})
        return helpers.call_action("resource_create", **kwargs)


@pytest.fixture
def resource_factory():
    return ResourceFactory


@pytest.fixture
def resource():
    return ResourceFactory()


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
def user_factory():
    return factories.User


@pytest.fixture
def clean_db(reset_db):
    reset_db()
    ytp_model.init_tables()


@pytest.fixture
def mock_storage(monkeypatch, ckan_config, tmpdir):
    monkeypatch.setitem(ckan_config, u'ckan.storage_path', str(tmpdir))
    monkeypatch.setattr(uploader, u'get_storage_path', lambda: str(tmpdir))


class Comment(factory.Factory):
    """A factory class for creating ytp comment. It must accept user_id and
    package_name, because I don't want to create extra entities in database
    during tests"""

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
