import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')

import django
django.setup()

from core.templatetags.currency_tags import format_currency
from django.template import Context

# Test with USD (should show original price)
context_usd = Context({'user_currency': 'USD', 'available_currencies': []})
result_usd = format_currency(context_usd, 1999.00)
print("USD 1999 result:", repr(result_usd))
print("USD 1999 starts with $:", result_usd.startswith('$'))

# Test with BDT (should convert)
context_bdt = Context({'user_currency': 'BDT', 'available_currencies': []})
result_bdt = format_currency(context_bdt, 1999.00)
print("BDT 1999 result length:", len(result_bdt))
print("BDT 1999 first 3 chars:", result_bdt[:3])
print("BDT 1999 has BDT symbol:", result_bdt[0] == '৳' or result_bdt.startswith('৳'))

# Test with available_currencies from DB
from core.models import ExchangeRate
available = list(ExchangeRate.objects.all())
context_mixed = Context({'user_currency': 'BDT', 'available_currencies': available})
result_mixed = format_currency(context_mixed, 1999.00)
print("BDT with DB rates result length:", len(result_mixed))
print("BDT with DB rates first 3 chars:", result_mixed[:3])