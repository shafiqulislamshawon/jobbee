from django.contrib import admin
from .models import HeroSectionSettings, CurrencySettings, Service, TrustedCompany

@admin.register(HeroSectionSettings)
class HeroSectionSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HeroSectionSettings.objects.exists()

@admin.register(CurrencySettings)
class CurrencySettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not CurrencySettings.objects.exists()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)

@admin.register(TrustedCompany)
class TrustedCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
