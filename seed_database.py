import os
import django
import subprocess

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from core.models import ExchangeRate, CurrencySettings, HeroSectionSettings, Service

User = get_user_model()

print("--- Starting Database Seeder ---")

# 1. Create Superuser
username = "codewithshawon"
email = "codewithshawon@gmail.com"
password = "1110215820"

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print(f"Superuser {username} already exists.")

# 2. Configure Default Site
site, created = Site.objects.get_or_create(id=1)
site.domain = 'jobbee.com'
site.name = 'JobBee'
site.save()
print("Configured Site ID=1")

# 3. Seed Exchange Rates
rates = {
    'BDT': 1,
    'USD': 120,
    'EUR': 130,
    'GBP': 150,
    'INR': 1.4,
    'CAD': 87,
    'AUD': 77,
}

for curr, rate in rates.items():
    ExchangeRate.objects.update_or_create(
        currency=curr,
        defaults={'rate_to_base': rate}
    )
print("Seeded Exchange Rates")

# 4. Currency Settings
CurrencySettings.objects.get_or_create(
    id=1,
    defaults={
        'base_currency': 'BDT',
        'base_currency_symbol': '৳',
        'display_currency': 'BDT',
        'display_currency_symbol': '৳',
        'exchange_rate': 1.0000,
        'enable_conversion': True
    }
)
print("Seeded Currency Settings")

# 5. Hero Section Settings
HeroSectionSettings.objects.get_or_create(id=1)
print("Seeded Hero Section Settings")

# 6. Default Services
services = [
    {
        'title': 'Job Posting',
        'description': 'Reach thousands of qualified candidates instantly. Our advanced matching algorithms ensure your job reaches the right audience.',
        'icon_svg': '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>',
        'order': 1
    },
    {
        'title': 'Employer Branding',
        'description': 'Showcase your company culture and build a strong employer brand with rich company profiles and employee testimonials.',
        'icon_svg': '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>',
        'order': 2
    },
    {
        'title': 'Talent Sourcing',
        'description': 'Proactively search and connect with passive candidates using our comprehensive talent pool and smart filters.',
        'icon_svg': '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>',
        'order': 3
    }
]

for srv in services:
    Service.objects.update_or_create(
        title=srv['title'],
        defaults={'description': srv['description'], 'icon_svg': srv['icon_svg'], 'order': srv['order']}
    )
print("Seeded Default Services")

# 7. Run other seed scripts
print("Running additional seed scripts...")
scripts = [
    'seed_categories.py',
    'seed_addons.py',
    'seed_plans.py',
    'seed_blog.py'
]

for script in scripts:
    if os.path.exists(script):
        print(f"Executing {script}...")
        subprocess.run(['python3', script])
    else:
        print(f"Warning: {script} not found, skipping.")

print("--- Database Seeding Complete! ---")
