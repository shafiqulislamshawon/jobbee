import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction

from accounts.models import User, EmployerProfile, SeekerProfile
from jobs.models import Job, Application, JobEngagement
from blog.models import Category, Post
from subscriptions.models import Plan, EmployerSubscription
from subscriptions.management.commands.seed_addons import Command as SeedAddonsCommand

# Data arrays for realistic multi-country/currency setups
COUNTRIES = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'IN', 'JP', 'BR', 'ZA']
CURRENCIES = ['USD', 'GBP', 'CAD', 'AUD', 'EUR', 'EUR', 'INR', 'JPY', 'BRL', 'ZAR']

JOB_TITLES = [
    "Senior Software Engineer", "Product Manager", "UX Designer", 
    "Data Scientist", "Marketing Director", "Sales Executive",
    "DevOps Engineer", "Cloud Architect", "HR Business Partner",
    "Financial Analyst", "Operations Manager", "Customer Success Specialist"
]

EMPLOYER_NAMES = [
    "Acme Corp", "TechNova", "Global Dynamics", "Stark Industries",
    "Wayne Enterprises", "Umbrella Corp", "Cyberdyne Systems",
    "Massive Dynamic", "Initech", "Hooli", "Pied Piper", "Aviato"
]

class Command(BaseCommand):
    help = 'Seeds massive realistic data for Jobbee'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting massive seeding...")

        # 1. Base Setup
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        # 2. Addons & Plans
        SeedAddonsCommand().handle()
        
        plan1, _ = Plan.objects.get_or_create(name='Starter', defaults={'price': 49.00, 'job_limit': 1, 'duration_days': 30})
        plan2, _ = Plan.objects.get_or_create(name='Business', defaults={'price': 149.00, 'job_limit': 5, 'duration_days': 30, 'has_banner': True})
        plan3, _ = Plan.objects.get_or_create(name='Enterprise', defaults={'price': 499.00, 'job_limit': -1, 'duration_days': 30, 'has_banner': True, 'can_feature_jobs': True, 'has_verification_badge': True})
        plans = [plan1, plan2, plan3]

        # 3. Create Employers (1000)
        self.stdout.write("Generating Employers...")
        employer_users = []
        employer_profiles = []
        pw = make_password("password123")
        
        for i in range(1000):
            emp_name = f"{random.choice(EMPLOYER_NAMES)} {i}"
            user = User(
                username=f"employer{i}",
                email=f"employer{i}@example.com",
                password=pw,
                is_employer=True
            )
            employer_users.append(user)
            
        User.objects.bulk_create(employer_users, batch_size=500)
        employer_users = list(User.objects.filter(is_employer=True, is_superuser=False))
        
        for user in employer_users:
            employer_profiles.append(EmployerProfile(
                user=user,
                company_name=f"Company {user.id}",
                industry=random.choice(["Tech", "Finance", "Healthcare", "Retail"]),
                company_size=random.choice(['1-10', '11-50', '51-200', '201-500', '500+']),
                is_verified=random.choice([True, False])
            ))
        EmployerProfile.objects.bulk_create(employer_profiles, batch_size=500)
        
        # Assign plans
        employer_profiles = list(EmployerProfile.objects.all())
        subs = []
        for profile in employer_profiles:
            subs.append(EmployerSubscription(
                employer=profile,
                plan=random.choice(plans),
                end_date=timezone.now() + timedelta(days=30),
                status='ACTIVE'
            ))
        EmployerSubscription.objects.bulk_create(subs, batch_size=500)

        # 4. Create Seekers (10000)
        self.stdout.write("Generating Seekers...")
        seeker_users = []
        seeker_profiles = []
        for i in range(10000):
            user = User(
                username=f"seeker{i}",
                email=f"seeker{i}@example.com",
                password=pw,
                first_name=f"First{i}",
                last_name=f"Last{i}",
                is_seeker=True
            )
            seeker_users.append(user)
            
        User.objects.bulk_create(seeker_users, batch_size=2000)
        seeker_users = list(User.objects.filter(is_seeker=True))
        
        for user in seeker_users:
            seeker_profiles.append(SeekerProfile(
                user=user,
                skills=random.choice(["Python, Django", "React, Node", "Sales, Marketing", "Design, Figma"]),
                gender=random.choice(['M', 'F', 'O', 'P']),
                age_group=random.choice(['18-24', '25-34', '35-44', '45-54', '55+']),
                location=random.choice(COUNTRIES)
            ))
        SeekerProfile.objects.bulk_create(seeker_profiles, batch_size=2000)

        # 5. Create Jobs (50000)
        self.stdout.write("Generating 50,000 Jobs...")
        jobs = []
        now = timezone.now()
        emp_list = list(User.objects.filter(is_employer=True))
        
        for i in range(50000):
            idx = random.randint(0, 9)
            jobs.append(Job(
                employer=random.choice(emp_list),
                title=f"{random.choice(JOB_TITLES)} - {i}",
                description="This is a realistic job description for a high-quality position.",
                responsibilities="Lead projects, write code, mentor juniors.",
                requirements="5+ years experience, BS in CS, strong communication.",
                currency=CURRENCIES[idx],
                salary_min=random.randint(40000, 80000),
                salary_max=random.randint(90000, 200000),
                employment_type=random.choice(['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP']),
                remote_status=random.choice(['REMOTE', 'HYBRID', 'ON_SITE']),
                location=COUNTRIES[idx],
                skills="Python, React, AWS",
                is_active=random.choice([True, True, False]),
                views_count=random.randint(0, 100),
                is_featured=random.choice([True, False, False, False]),
                created_at=now - timedelta(days=random.randint(0, 30))
            ))
            
            if len(jobs) == 5000:
                Job.objects.bulk_create(jobs)
                self.stdout.write(f"Inserted {i+1} jobs...")
                jobs = []
        
        if jobs:
            Job.objects.bulk_create(jobs)

        # 6. Blog Posts (500)
        self.stdout.write("Generating Blog Posts...")
        cat1, _ = Category.objects.get_or_create(name="Tech", slug="tech")
        cat2, _ = Category.objects.get_or_create(name="Career", slug="career")
        cats = [cat1, cat2]
        
        posts = []
        for i in range(500):
            posts.append(Post(
                title=f"Blog Post {i} - International Tech Trends",
                slug=f"blog-post-{i}-{uuid.uuid4().hex[:6]}",
                author=random.choice(emp_list),
                category=random.choice(cats),
                content="This is a detailed analysis of the global job market across multiple timezones and currencies.",
                status='published',
                created_at=now - timedelta(days=random.randint(0, 100))
            ))
        Post.objects.bulk_create(posts, batch_size=250)

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
