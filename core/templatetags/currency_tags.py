from django import template
from core.models import CurrencySettings

register = template.Library()

@register.filter
def currency(value):
    if value is None or value == '':
        return ''
        
    try:
        amount = float(value)
    except (ValueError, TypeError):
        return value
        
    settings = CurrencySettings.objects.first()
    
    if not settings or not settings.enable_conversion:
        # Default fallback if no settings or conversion is off
        symbol = settings.base_currency_symbol if settings else '$'
        return f"{symbol} {amount:,.2f}"
        
    converted_amount = amount * float(settings.exchange_rate)
    return f"{settings.display_currency_symbol} {converted_amount:,.2f}"
