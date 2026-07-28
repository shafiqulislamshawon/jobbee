from django.conf import settings
from .models import HeroSectionSettings, TrustedCompany, CurrencySettings

def site_settings(request):
    hero_settings = HeroSectionSettings.objects.first()
    trusted_companies = TrustedCompany.objects.all()
    currency_settings = CurrencySettings.objects.first()
    
    return {
        'SITE_NAME': 'Jobbee',
        'site_settings': {'site_name': 'Jobbee'},
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'hero_settings': hero_settings,
        'trusted_companies': trusted_companies,
        'currency_settings': currency_settings,
    }
