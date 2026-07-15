from django.contrib import admin
from .models import Job, Application
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Job)
class JobAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'employer', 'created_at')
    list_filter = ('employment_type', 'remote_status', 'created_at')
    search_fields = ('title', 'employer__company_name')

@admin.register(Application)
class ApplicationAdmin(SimpleHistoryAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('job__title', 'applicant__username')
