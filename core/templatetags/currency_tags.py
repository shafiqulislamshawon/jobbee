from django import template
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
        
    user_currency = context.get('user_currency', 'USD')
    available_currencies = context.get('available_currencies', None)
    
    # Base USD symbol is $
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
    
    target_symbol = symbols.get(user_currency, '$')
    
    # If user currency is USD (base), just return
    if user_currency == 'USD':
        return f"{target_symbol} {amount:,.0f}"
        
    # Get conversion rate
    rate = 1.0
    if available_currencies:
        for ex in available_currencies:
            if ex.currency == user_currency:
                rate = float(ex.rate_to_base)
                break
    else:
        # Fallback to direct DB query if context processor didn't provide it (e.g. in emails)
        ex = ExchangeRate.objects.filter(currency=user_currency).first()
        if ex:
            rate = float(ex.rate_to_base)
            
    converted_amount = amount * rate
    return f"{target_symbol} {converted_amount:,.0f}"
