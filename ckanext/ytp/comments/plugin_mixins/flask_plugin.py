# encoding: utf-8

import ckan.plugins as p

from ckanext.ytp.comments.cli import click_cli
from ckanext.ytp.comments.controllers import blueprints


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return blueprints.get_blueprints()

    # IClick

    def get_commands(self):
        return click_cli.get_commands()
