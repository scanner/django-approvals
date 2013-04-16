#
# File: $Id: forms.py 12 2008-10-06 08:57:13Z scanner $
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
from django.contrib.auth.models import User
from approvals.models import Approval

# Try to import the django-based registration app. This is used down below
# to subclass the registrations's RegistrationForm such that it hooks
# in to our approval process.
try:
    import registration
except ImportError:
    registration = None

####################################################################
#
class ApprovalForm(forms.Form):
    """
    To act on an approval you need to either mark it as approved or not.
    This is a simple base form with a single boolean field to do that.
    """
    approved = forms.NullBooleanField(label = _('approved'), required = True)
    reason = forms.CharField(label = _('reason'), max_length = 2048,
                             required = False)

####################################################################
#
if registration:
    # If we managed to import the django-based registration app then subclass
    # its RegistrationForm to hook in to our approval process.
    #
    from registration.models import RegistrationProfile
    from registration.forms import RegistrationForm

    ####################################################################
    #
    class RegistrationFormNeedsApproval(RegistrationForm):
        """
        Form for registering a new account, but mark it for needing
        approval.  This is done by override the save() method so that
        when it creates an inactive user it does NOT send email, and
        creates an approval object.
        """

        ######################################################################
        #
        def save(self, profile_callback = None):
            """
            Create the new 'User', 'RegistrationProfile', and 'Approval'
            object.

            This is essentially a light wrapper around
            ``RegistrationProfile.objects.create_inactive_user()``, feeding it
            the form data and a profile callback (see the documentation on
            ``create_inactive_user()`` for details) if supplied.

            """
            new_user = registration.models.RegistrationProfile.objects.create_inactive_user(\
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1'],

                # We do not send an email but this parameter is required.
                #
                email=self.cleaned_data['email'],
                profile_callback=profile_callback,
                send_email = False)

            reg_profile = RegistrationProfile.objects.get(user = new_user)
            new_approval = Approval(needs_approval = reg_profile)
            new_approval.save()
            return new_user

    ####################################################################
    #
    class RegistrationFormUniqueEmailNeedsApproval(RegistrationFormNeedsApproval):
        """
        Just like RegistrationFormUniqueEmail except they will require
        an approval before they are sent their registration
        email. This is done by overriding the save() method so that when
        it creates an inactive user it does NOT send email, and
        creates an approval object.
        """

        ####################################################################
        #
        def clean_email(self):
            """
            Validate that the supplied email address is unique for the
            site.

            """
            try:
                user = User.objects.get(email__iexact=self.cleaned_data['email'])
            except User.DoesNotExist:
                return self.cleaned_data['email']
            except User.MultipleObjectsReturned:
                pass
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.')
                                        )
