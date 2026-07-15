from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmployerProfile, SeekerProfile, Education, Experience, Certification
from simple_history.admin import SimpleHistoryAdmin

class CustomUserAdmin(SimpleHistoryAdmin, UserAdmin):
    list_display = ('username', 'email', 'is_employer', 'is_seeker', 'is_staff')
    list_filter = ('is_employer', 'is_seeker', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('is_employer', 'is_seeker')}),
    )

@admin.register(EmployerProfile)
class EmployerProfileAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'company_name', 'website', 'verification_status', 'is_verified')
    list_filter = ('verification_status', 'is_verified')
    search_fields = ('company_name', 'user__username', 'user__email')
    actions = ['approve_verification', 'reject_verification']
    
    def approve_verification(self, request, queryset):
        queryset.update(verification_status='APPROVED', is_verified=True)
    approve_verification.short_description = "Approve selected verifications"
    
    def reject_verification(self, request, queryset):
        queryset.update(verification_status='REJECTED', is_verified=False)
    reject_verification.short_description = "Reject selected verifications"

@admin.register(SeekerProfile)
class SeekerProfileAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'location', 'resume_score')
    search_fields = ('user__username', 'user__email', 'skills')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Certification)
