# encoding: utf-8

import ckan.plugins as p
from ckanext.ytp.comments.cli import click_cli


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IClick)

    # IClick

    def get_commands(self):
        return click_cli.get_commands()
