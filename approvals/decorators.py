#
# File: $Id: decorators.py 8 2008-09-29 05:17:33Z scanner $
#
"""
Useful decorators for restricting who has access to all of the pending approvals.
"""

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

###########################################################################
#
def is_staff(function = None):
    """
    Decorator for views in the approvals app. We require that the someone
    must be staff for them to see and act upon Approval objects.
    """
    actual_decorator = user_passes_test(lambda u: u.is_staff,
                                        login_url = settings.LOGIN_URL)
    if function:
        return actual_decorator(function)
    return actual_decorator

