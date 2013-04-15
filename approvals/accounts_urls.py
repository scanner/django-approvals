"""
URLConf for Django user registration and authentication.

Recommended usage is a call to ``include()`` in your project's root
URLConf to include this URLConf for any URL beginning with
``/accounts/``.

This is based on the urls.py from the james bennett's registration
application. It for the most part is identical.

The changes are for passing custom templates and forms in to the registration
URL.
"""


from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from django.views.generic.list_detail import object_list

from registration.views import activate
from registration.views import register

from approvals.forms import RegistrationFormNeedsApproval

# We import the 'approval_acted_on' signal from approvals.models and then
# we register a handler for it. This is so that we can now when approvals
# have been acted upon, and if the approval is for a RegistrationProfile
# object (as created by RegistrationFormNeedsApproval) we can decide
# whether or not to send the registration activation email.
#
from approvals.models import approval_acted_on, Approval
from approvals.decorators import is_staff
from approvals.actions import register_user

approval_acted_on.connect(register_user)

##########################
#
urlpatterns = patterns(
    '',
    # Activation keys get matched by \w+ instead of
    # the more specific [a-fA-F0-9]{40} because a
    # bad activation key should still get to the
    # view; that way it can return a sensible
    # "invalid key" message instead of a confusing
    # 404.
    #
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        name='registration_activate'),
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
    url(r'^register/$',
        register,
        {'form_class' : RegistrationFormNeedsApproval },
        name='registration_register'),
    url(r'^register/complete/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^approval/$',
        is_staff(object_list),
        { 'queryset' : Approval.objects.filter(approved = None).filter(content_type__app_label = 'registration'),
          'paginate_by' : 20,
          'template_name' : 'registration/approvals_list.html'},
        name = 'registration_approvals_list'),
    )
