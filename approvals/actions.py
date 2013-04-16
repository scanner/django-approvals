#
# File: $Id: actions.py 4 2008-09-15 02:44:56Z scanner $
#
"""
This module contains some action functions that can be invoked by the
`approvals.models.approval_acted_on` signal.

These serve partly as working examples and also the initial case that
the `approvals` app was written for: Requiring approval for a user
registration.
"""

from django.utils.translation import ugettext_lazy as _

# The `register_user` method is only defined if we can import the
# `registration` app.
#
try:
    from registration.models import RegistrationProfile
except ImportError:
    RegistrationProfile = None

if RegistrationProfile:
    ##########################################################################
    #
    def register_user(sender, **kwargs):
        """
        This signal handler is meant to be connected to the
        `approvals.models.approval_acted_on` signal. It indicates that a
        specific Approval object (the `sender` argument) has been acted
        upon. This function checks to see if the object that is being
        approved or not is a registration.models.RegistrationProfile. If
        it is and if it was approved we invoke the 'send_email()' method
        on that object to send the registration email off to the
        soon-to-be new user. If it was not approved then nothing is done.

        XXX Perhaps we should have a keyword argument that indicates that
            we should send the 'reason' message to the email address of
            the user being denied.

        Arguments:
        - `sender`:   The approvals.models.Approval object that was acted on.
        - `**kwargs`: The `approval_acted_on` signal has no key word
                      arguments at this time.
        """

        # If this was not approved or if the `needs_approval` object
        # is not of a type that we care about, ie: not a
        # registrations.models.RegistrationProfile object, then do nothing.
        #
        if not isinstance(sender.needs_approval, RegistrationProfile):
            return

        # We break out 'none' 'false'  and 'true' cases so that we can
        # send different messages.
        #
        if sender.approved is None:
            message = _("No approval action taken for %s") % \
                sender.needs_approval
        elif sender.approved is False:
            message = _("Approval denied for %s") % sender.needs_approval
        else:
            # Finally, we know this is a successful approval for a
            # registration profile. Make our user-to-be happy.
            #
            sender.needs_approval.send_email()
            message = _("Account for '%s' was approved.") % \
                sender.needs_approval

        sender.acted_on_by.message_set.create(message = message)
        return
