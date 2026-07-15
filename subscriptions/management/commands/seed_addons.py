import os
from django.core.management.base import BaseCommand
from subscriptions.models import AddOn

class Command(BaseCommand):
    help = 'Seed AddOn store items'

    def handle(self, *args, **kwargs):
        addons = [
            {'name': 'Featured Job (10 Days)', 'price': 999, 'addon_type': 'FEATURED_JOB', 'description': 'Make your job stand out in search results for 10 days.'},
            {'name': 'Extra Starter Job Post', 'price': 500, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Starter plan.'},
            {'name': 'Extra Business Job Post', 'price': 1000, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Business plan.'},
            {'name': 'Extra Enterprise Job Post', 'price': 1500, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Enterprise plan.'},
            {'name': 'Homepage Banner', 'price': 2999, 'addon_type': 'BANNER', 'description': 'Display your company banner prominently on the homepage.'},
            {'name': 'Facebook Promotion', 'price': 1499, 'addon_type': 'SOCIAL_PROMO', 'description': 'We will promote your job on our Facebook page.'},
            {'name': 'LinkedIn Promotion', 'price': 1999, 'addon_type': 'SOCIAL_PROMO', 'description': 'We will promote your job on our LinkedIn network.'},
            {'name': 'CV Database Access (100 CVs)', 'price': 2499, 'addon_type': 'CV_DB', 'description': 'Unlock contact information for 100 candidates from our CV database.'},
            {'name': 'Candidate Shortlisting Service', 'price': 4999, 'addon_type': 'SHORTLISTING', 'description': 'Let our expert recruiters shortlist the best candidates for you.'},
            {'name': 'Employer Verification Badge', 'price': 999, 'addon_type': 'VERIFICATION', 'description': 'Instantly get the verified badge next to your company name.'},
        ]

        for data in addons:
            AddOn.objects.update_or_create(
                name=data['name'],
                defaults=data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded AddOns'))
