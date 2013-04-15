#
# File: $Id: views.py 11 2008-09-29 06:25:36Z scanner $
#

# Django imports
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

# Form imports
#
from approvals.forms import ApprovalForm

# Model imports
#
from approvals.models import Approval

#############################################################################
#
def act_on_approval(request, object_id,
                    template_name = 'approvals/act_on_approval.html',
                    form_class = ApprovalForm,
                    extra_context = None):
    """
    Act on an approval object. This view presents an approval object
    with a form that lets the user approve or disapprove of an
    approval if it has not been acted upon yet.

    Arguments:
    - `request`: Django request object.
    - `object_id`: The id of the approval object to view.
    - `template_name`: Path to the template to use.
    - `extra_context`: Dictionary of extra context data to pass to the template.
    """
    object = get_object_or_404(Approval, pk = object_id)

    # See if an approval is being acted upon by the approval form being
    # posted. If we have a valid approval form then invoke the approve method
    # on our object with the approval status and reason from the form.
    #
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            if 'reason' in form.cleaned_data:
                reason = form.cleaned_data['reason']
            else:
                reason = None

            object.approve(form.cleaned_data['approved'], request.user, reason)

            if request.user.is_authenticated():
                request.user.message_set.create(message = _("Approval '%s' "
                                                            "processed") % \
                                                    object)
            return HttpResponseRedirect(reverse('approvals_act_on',
                                                args = [object.id]))
    else:
        form = form_class({'approved': object.approved,
                           'reason':object.reason })

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form'  : form,
                                'object': object},
                              context_instance=context)
