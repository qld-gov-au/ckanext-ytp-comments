from ckan.common import c
from ckan.lib.base import render
from ckan.logic import check_access, get_action
from ckanext.datarequests import actions


def get_content_item(content_type, context, data_dict):
    if content_type == 'datarequest':
        c.datarequest = actions.show_datarequest(context, data_dict)
    else:
        data_dict['include_tracking'] = True
        c.pkg_dict = get_action('package_show')(context, data_dict)
        c.pkg = context['package']


def check_content_access(content_type, context, data_dict):
    if content_type == 'dataset':
        check_access('package_show', context, data_dict)
    elif content_type == 'datareqest':
        check_access('show_datarequest', context, data_dict)


def get_redirect_url(content_type, content_item_id, anchor):
    if content_type == 'datarequest':
        return str('/datarequest/comment/%s#%s' % (content_item_id, anchor))
    else:
        return str('/dataset/%s#%s' % (content_item_id, anchor))


def render_content_template(content_type):
    return render(
        'datarequests/comment.html' if content_type == 'datarequest' else "package/read.html"
    )
