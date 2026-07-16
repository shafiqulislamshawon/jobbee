from django.contrib import admin
from .models import HeroSectionSettings

@admin.register(HeroSectionSettings)
class HeroSectionSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow adding if there are no existing objects
        return not HeroSectionSettings.objects.exists()

