from django.conf import settings
from .models import HeroSectionSettings, TrustedCompany, CurrencySettings, ExchangeRate

def site_settings(request):
    hero_settings = HeroSectionSettings.objects.first()
    trusted_companies = TrustedCompany.objects.all()
    currency_settings = CurrencySettings.objects.first()
    available_currencies = ExchangeRate.objects.all()
    
    # Default to BDT if not set in session
    user_currency = request.session.get('user_currency', 'BDT')
    
    return {
        'SITE_NAME': 'Jobbee',
        'site_settings': {'site_name': 'Jobbee'},
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'hero_settings': hero_settings,
        'trusted_companies': trusted_companies,
        'currency_settings': currency_settings,
        'available_currencies': available_currencies,
        'user_currency': user_currency,
    }
