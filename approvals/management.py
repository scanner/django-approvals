#
# File: $Id: management.py 4 2008-09-15 02:44:56Z scanner $
#
"""
This is part of the management command suite for the approvals module.

Very little happens in here right now. The main purpose is that if the
'notification' module is importable then we create a notice type for
'approvals' so that we can create a notice whenever an approval is
created.

XXX Eventually we will may add some methods to go through pending approvals
    that match some query set and send out reminders that those approvals
    are still waiting for someone to act on them.

    We need more information about how approvals may be used before we
    figure out the specifics of those methods.
"""
from django.db.models.signals import post_syncdb

# If we are able to import the 'notification' module then attach a
# hook to the 'post_syncdb' signal that will create a new notice type
# for approvals. This lets us hook in to the notification framework to
# keep track of approvals instead of only using email.
#
try:
    from notification import models as notification

    ########################################################################
    #
    def create_notice_types(sender, **kwargs):
        notification.create_notice_type("pending_approvals",
                                        "Pending Approval",
                                        "There is a new action requiring "
                                        "approval.")
        return

    ########################################################################
    #
    post_syncdb.connect(create_notice_types)

except ImportError:
    print "Skipping creation of NoticeTypes as notification app not found"

