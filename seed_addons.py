import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
django.setup()

from subscriptions.models import AddOn

def seed_addons():
    addons_data = [
        {
            'name': 'Featured Job Post',
            'price': 49.99,
            'description': 'Highlight your job posting at the top of search results for 7 days.',
            'addon_type': 'FEATURED_JOB'
        },
        {
            'name': 'Extra Job Post',
            'price': 19.99,
            'description': 'Purchase an additional job post if you have reached your plan limit.',
            'addon_type': 'EXTRA_JOB'
        },
        {
            'name': 'Urgent Hiring Tag',
            'price': 29.99,
            'description': 'Add an "Urgent" tag to your job to attract immediate candidates.',
            'addon_type': 'URGENT_TAG'
        },
        {
            'name': 'Access to CV Database (1 Day)',
            'price': 99.99,
            'description': 'Get 24-hour access to browse and contact candidates from our CV database.',
            'addon_type': 'CV_ACCESS'
        }
    ]

    for data in addons_data:
        addon, created = AddOn.objects.get_or_create(
            name=data['name'],
            defaults={
                'price': data['price'],
                'description': data['description'],
                'addon_type': data['addon_type']
            }
        )
        if created:
            print(f"Created AddOn: {addon.name}")
        else:
            # Update existing
            addon.price = data['price']
            addon.description = data['description']
            addon.addon_type = data['addon_type']
            addon.save()
            print(f"Updated AddOn: {addon.name}")

if __name__ == '__main__':
    seed_addons()
    print("Addons seeded successfully.")
