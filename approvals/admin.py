from django.contrib import admin

from approvals.models import Approval


class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'created', 'content_type')
    list_filter = ('approved', 'created', 'when_acted_on', 'content_type')
    search_fields = ('acted_on_by__username', 'acted_on_by__first_name',
                     'reason')

admin.site.register(Approval, ApprovalAdmin)
