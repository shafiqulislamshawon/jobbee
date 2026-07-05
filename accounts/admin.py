from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmployerProfile, SeekerProfile, Education, Experience, Certification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_employer', 'is_seeker', 'is_staff')
    list_filter = ('is_employer', 'is_seeker', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles', {'fields': ('is_employer', 'is_seeker')}),
    )

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'website')
    search_fields = ('company_name', 'user__username', 'user__email')

@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'portfolio_url')
    search_fields = ('user__username', 'user__email', 'skills')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Certification)
