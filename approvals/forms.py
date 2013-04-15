#
# File: $Id: forms.py 15 2010-12-03 15:48:53Z scanner $
#
"""
Forms for use by the django-based approvals app.

The approvals app provides a somewhat generic interface for having a
class of users approve some items that are pending approval.

We also provide a subclass of the registration app form if the
registration module can be imported which creates a form that requires
approvals for membership registrations.

"""

# Django imports
#
from django import forms
from django.utils.translation import ugettext_lazy as _

# Model imports
#
from approvals.models import Approval

####################################################################
#
class ApprovalForm(forms.Form):
    """
    To act on an approval you need to either mark it as approved or not.
    This is a simple base form with a single boolean field to do that.
    """
    approved = forms.NullBooleanField(label = _('Approved'), required = True)
    reason = forms.CharField(label = _('Reason'), max_length = 2048,
                             required = False)
