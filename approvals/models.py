#
# File: $Id: models.py 15 2010-12-03 15:48:53Z scanner $
#

# Python standard imports
import datetime

# Django imports
#
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
import django.dispatch

# Model imports
#
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# If the django-notification app is present then import and we will use this
# instead of sending email directly.
#
try:
    from notification import models as notification
except ImportError:
    notification = None

# favour django-mailer but fall back to django.core.mail
try:
    from mailer import send_mail
except ImportError:
    from django.core.mail import send_mail

# We define a signal that is invoked whenever an Approval object
# is acted upon (by calling its 'approve()' method.
#
approval_acted_on = django.dispatch.Signal()

####################################################################
#
class Approval(models.Model):
    """
    This object represents some other object in the database

    XXX Right now we assume that the people that need to approve something
        must have the is_staff bit set. We should make it so that you can
        specify a list of who is allowed to approve something.
    """
    approved = models.NullBooleanField(_('approved'), null = True,
                                       help_text = _("Has the 'needs_approval' "
                                       "object been approved, turned down, or "
                                       "not acted on yet."))
    acted_on_by = models.ForeignKey(User, null = True, blank = True,
                                    verbose_name = _('acted on by'),
                                    help_text = _("If this approval has been "
                                    "acted on, this will be the user that "
                                    "has made the decision."))
    created = models.DateTimeField(_('created'), db_index = True,
                                   auto_now_add = True)
    modified = models.DateTimeField(_('modified'), auto_now = True)
    when_acted_on = models.DateTimeField(_('when acted on'),null = True,
                                         blank = True)
    reason = models.TextField(_('reason'), max_length = 2048, blank = True,
                              null = True,
                              help_text = _("When an object is approved or "
                              "disapproved the person doing the action "
                              "can supply some reason here."))

    # The generic foreign key relation. These three fields let us
    # relate an Approval object to any other model out there
    # XXX As long as that other model uses an integer as its primary
    #     key due to the type of 'object_id'
    #
    content_type = models.ForeignKey(ContentType,
                                     verbose_name = _("content type"))
    object_id = models.PositiveIntegerField(_('object id'))
    needs_approval = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('approval')
        verbose_name_plural = _('approvals')
        ordering = ['created']

    ####################################################################
    #
    def __unicode__(self):
        if self.approved is None:
            appr = 'pending'
        elif self.approved:
            appr = 'approved'
        else:
            appr = 'denied'
        return u"%d, %s, %s" % (self.id, appr, str(self.needs_approval))

    ####################################################################
    #
    @permalink
    def act_on_url(self):
        """
        A helper method that will return the URL that will bring up
        the 'act on this approval' url.
        """
        return ("approvals_act_on", [str(self.id)])

    ####################################################################
    #
    def save(self, force_insert = False, force_update = False):
        """
        We override the `save()` method so that when an Approval is
        being saved for the first time we can send a message to the
        is_staff members that there is a new item requiring their
        attention.

        Arguments:

        - `force_insert`: - passed through to the parent class method
        - `force_update`: - passed through to the parent class method
        """

        # We send our notification to the staff after we have saved
        # the approval for the first time, we need an id to construct
        # the URL for it.
        #
        if self.id is None:
            new = True
        else:
            new = False

        super(Approval, self).save(force_insert, force_update)

        if new:
            # Now we send an email message to our site admins. If we have
            # the django-notification app installed use that to send
            # the message out (because it also creates notification
            # objects.) Otherwise, use django's built in emailer.
            #
            current_site = Site.objects.get_current()
            subject = render_to_string('approvals/approval_request_subj.txt',
                                       { 'site'     : current_site,
                                         'approval' : self })

            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())

            # XXX django-mailer defines a limit of 100 characters
            #     for a subject. We could change that, but better to be
            #     safe and truncate subjects that are over 100 characters
            #     here.
            if len(subject) > 100:
                subject = subject[0:99]

            message = render_to_string('approvals/approval_request_email.txt',
                                       { 'site'     : current_site,
                                         'approval' : self })
            if notification:
                notification.send(User.objects.filter(is_staff = True),
                                  "pending_approvals",
                                  { 'message' : message,
                                    'subject' : subject,
                                    'site'    : current_site,
                                    'approval': self })
            else:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                          User.objects.filter(is_staff = True))
        return

    ####################################################################
    #
    def approve(self, approval_status, approver, reason = None):
        """
        This method does the work to mark an Approval as 'approved' or
        not.  It will update the object with its approval status (the
        'approved' field gets set), who acted on this Approval, and when it
        was approved.

        NOTE: This will cause the Approval instance to be saved to the
              database.

        NOTE: This will cause the `approval_acted_on` signal to be
              sent.  it is expected that other applications wanting to
              act on something be approved or not will listen for this
              signal and see if the object being acted upon is one
              that they care about.

        XXX We should probably only let an approval be set once.

        Arguments:
        - `approval_status`: Boolean - is this approved or not.
        - `approver`: User - the user that is acting on this approval.
        - `reason`: A string to set as the reason for accepting or denying
                    this approval request.
        """

        self.approved = approval_status
        self.acted_on_by = approver
        self.when_acted_on = datetime.datetime.utcnow()
        if reason:
            self.reason = reason

        self.save()

        approval_acted_on.send(sender = self)
        return

    ##################################################################
    #
    def processed(self):
        """
        A helper method that tells you whether or not this approval
        has already been acted on. Most UI's are going to want an
        approval to only be acted on once.
        """
        return self.approved is not None

