import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')

import django
django.setup

django.setup()

from core.context_processors import site_settings
import django.http

# Create a minimal request
req = django.http.HttpRequest()

# Call the context processor
try:
    result = site_settings(req)
    print("user_currency:", result.get('user_currency'))
    print("available_currencies count:", len(result.get('available_currencies', [])))
    if result.get('available_currencies'):
        for c in result.get('available_currencies', [])[:3]:
            print(' -', c.currency, 'rate:', c.rate_to_base)
except Exception as e:
    print("Error:", e)