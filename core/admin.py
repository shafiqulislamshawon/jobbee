from django.contrib import admin
from .models import HeroSectionSettings, CurrencySettings

@admin.register(HeroSectionSettings)
class HeroSectionSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HeroSectionSettings.objects.exists()

@admin.register(CurrencySettings)
class CurrencySettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not CurrencySettings.objects.exists()
