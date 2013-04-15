"""
URLConf for Django approvals app.

Recommended usage is a call to ``include()`` in your project's root
URLConf to include this URLConf for any URL beginning with
`/approvals/`.

"""
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from approvals.views import act_on_approval
from approvals.decorators import is_staff

from approvals.models import Approval

###########################################################################
#
urlpatterns = patterns(
    '',
    url(r'^(?P<object_id>\d+)/act_on/$',
        is_staff(act_on_approval),
        { 'template_name': 'approvals/act_on_approval.html' },
        name='approvals_act_on'),
    )
