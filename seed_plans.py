import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobbee.settings")
django.setup()

from subscriptions.models import Plan

Plan.objects.all().delete()

plans_data = [
    {
        "name": "Starter",
        "price": 1999.00,
        "job_limit": 1,
        "duration_days": 30,
        "best_for": "Small businesses & startups",
        "job_posts_text": "1 Active Job (30 Days)",
        "applications_text": "Unlimited",
        "cv_database_access": "Applicants Only",
        "featured_jobs_text": "—",
        "homepage_placement": False,
        "social_media_promotion": "—",
        "company_branding": "Logo + Basic Company Profile",
        "analytics_dashboard": "Basic",
        "dedicated_account_manager": False,
        "recruitment_consultation": False,
        "priority_customer_support": "Email",
        "remote_hybrid_support": False,
        "custom_hiring_campaigns": False,
    },
    {
        "name": "Business",
        "price": 9999.00,
        "job_limit": 10,
        "duration_days": 180,
        "best_for": "Growing companies & HR teams",
        "job_posts_text": "Up to 10 Active Jobs (30 days)",
        "applications_text": "Unlimited",
        "cv_database_access": "Full Applicant Access",
        "featured_jobs_text": "3 Featured Jobs",
        "homepage_placement": True,
        "social_media_promotion": "2 Campaigns / Month",
        "company_branding": "Logo + Company Banner",
        "analytics_dashboard": "Advanced Reports",
        "dedicated_account_manager": False,
        "recruitment_consultation": True,
        "priority_customer_support": "Priority WhatsApp & Email",
        "remote_hybrid_support": True,
        "custom_hiring_campaigns": False,
    },
    {
        "name": "Enterprise",
        "price": 24999.00,
        "job_limit": 30,
        "duration_days": 365,
        "best_for": "Large companies & recruitment agencies",
        "job_posts_text": "*Unlimited Job Posts (up to 30 jobs)",
        "applications_text": "Unlimited",
        "cv_database_access": "Premium CV Database Access",
        "featured_jobs_text": "Unlimited Featured Jobs",
        "homepage_placement": True,
        "social_media_promotion": "Unlimited Campaigns",
        "company_branding": "Premium Employer Branding",
        "analytics_dashboard": "Custom Analytics & Insights",
        "dedicated_account_manager": True,
        "recruitment_consultation": True,
        "priority_customer_support": "Dedicated Phone + WhatsApp",
        "remote_hybrid_support": True,
        "custom_hiring_campaigns": True,
    }
]

for p_data in plans_data:
    Plan.objects.create(**p_data)
    
print("Plans seeded successfully!")
