from django.contrib import admin
from .models import Job, Application

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'employment_type', 'is_active', 'views_count', 'created_at')
    list_filter = ('employment_type', 'remote_status', 'is_active')
    search_fields = ('title', 'description', 'employer__username')

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status',)
    search_fields = ('job__title', 'applicant__username')

admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
