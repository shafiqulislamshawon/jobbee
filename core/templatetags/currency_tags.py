from django import template
from django.utils.formats import localize
from core.models import CurrencySettings, ExchangeRate
from jobs.models import Job

register = template.Library()

@register.simple_tag(takes_context=True)
def format_currency(context, value):
    if value is None or value == '':
        return ''
        
    try:
        amount = float(value)
    except (ValueError, TypeError):
        return value
        
    user_currency = context.get('user_currency', 'BDT')
    available_currencies = context.get('available_currencies', None)
    
    # Base BDT symbol is ৳
    # If we need symbols for user_currency, we can use the Job.CURRENCY_CHOICES dictionary mapping we made.
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'C$',
        'AUD': 'A$',
        'INR': '₹',
        'BDT': '৳'
    }
    
    target_symbol = symbols.get(user_currency, '৳')
    
    # If user currency is BDT (base), just return
    if user_currency == 'BDT':
        return f"{target_symbol} {amount:,.0f}"
        
    # Get target currency rate
    target_rate = 1.0
    
    if available_currencies:
        for ex in available_currencies:
            if ex.currency == user_currency:
                target_rate = float(ex.rate_to_base)
                break
    else:
        # Fallback to direct DB query if context processor didn't provide it (e.g. in emails)
        ex_target = ExchangeRate.objects.filter(currency=user_currency).first()
        if ex_target:
            target_rate = float(ex_target.rate_to_base)
            
    if target_rate > 0:
        converted_amount = amount / target_rate
    else:
        converted_amount = amount
        
    return f"{target_symbol} {converted_amount:,.0f}"

@register.filter
def currency(value):
    context = template.Context({})
    return format_currency(context, value)
