import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, EmployerProfile, SeekerProfile
from jobs.models import Job, Application, JobEngagement
from blog.models import Category, Post

class Command(BaseCommand):
    help = 'Seeds the database with test data for Jobbee'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")

        # Clear existing data (optional, but good for fresh seeds)
        # We will not delete superusers, only regular users created by this script or previous runs
        User.objects.filter(is_superuser=False).delete()
        Job.objects.all().delete()
        JobEngagement.objects.all().delete()
        Category.objects.all().delete()
        Post.objects.all().delete()

        # 1. Create Employers
        employers_data = [
            {"email": "tech@google.com", "name": "Google", "industry": "Technology"},
            {"email": "careers@amazon.com", "name": "Amazon", "industry": "E-Commerce"},
            {"email": "hr@stripe.com", "name": "Stripe", "industry": "FinTech"},
            {"email": "jobs@airbnb.com", "name": "Airbnb", "industry": "Hospitality"},
            {"email": "hello@openai.com", "name": "OpenAI", "industry": "Artificial Intelligence"},
        ]
        
        employers = []
        for data in employers_data:
            user = User.objects.create_user(
                username=data["email"].split('@')[0],
                email=data["email"],
                password="password123",
                is_employer=True
            )
            # Create Employer Profile
            EmployerProfile.objects.create(
                user=user,
                company_name=data["name"],
                description=f"{data['name']} is a leading company in the {data['industry']} sector."
            )
            employers.append(user)
            self.stdout.write(f"Created employer: {data['name']}")

        # 2. Create Seekers
        seekers = []
        genders = ['M', 'F', 'O', 'P']
        ages = ['18-24', '25-34', '35-44', '45-54', '55+']
        
        for i in range(1, 16):
            user = User.objects.create_user(
                username=f"seeker{i}",
                email=f"seeker{i}@example.com",
                password="password123",
                first_name=f"John{i}",
                last_name=f"Doe{i}",
                is_seeker=True
            )
            SeekerProfile.objects.create(
                user=user,
                skills="Python, Django, JavaScript, React",
                gender=random.choice(genders),
                age_group=random.choice(ages)
            )
            seekers.append(user)
        self.stdout.write(f"Created {len(seekers)} job seekers.")

        # 3. Create Jobs
        job_titles = [
            "Senior Python Developer", "Frontend Engineer", "Full Stack Developer",
            "Data Scientist", "Machine Learning Engineer", "DevOps Specialist",
            "Product Manager", "UX/UI Designer", "Backend Architect", "Systems Administrator"
        ]
        employment_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP']
        remote_statuses = ['REMOTE', 'HYBRID', 'ON_SITE']
        locations = ["New York, NY", "San Francisco, CA", "London, UK", "Berlin, Germany", "Austin, TX"]

        jobs = []
        for _ in range(25):
            employer = random.choice(employers)
            job = Job.objects.create(
                employer=employer,
                title=random.choice(job_titles),
                description="We are looking for a highly skilled professional to join our dynamic team.",
                responsibilities="- Write clean, maintainable code\n- Collaborate with cross-functional teams",
                requirements="- 3+ years of experience\n- Strong problem-solving skills",
                salary_min=random.randint(60000, 90000),
                salary_max=random.randint(100000, 180000),
                employment_type=random.choice(employment_types),
                remote_status=random.choice(remote_statuses),
                location=random.choice(locations),
                skills="Python, React, AWS",
                is_active=random.choice([True, True, True, False]), # 75% active
                created_at=timezone.now() - timedelta(days=random.randint(0, 30))
            )
            # Update created_at (auto_now_add makes it tricky, so we update it post-creation if needed, but for Django 1.8+ it respects the value if provided sometimes, or we can use .update())
            Job.objects.filter(id=job.id).update(created_at=timezone.now() - timedelta(days=random.randint(0, 30)))
            jobs.append(job)
        self.stdout.write(f"Created {len(jobs)} jobs.")

        # 4. Create Applications and Engagements
        status_choices = ['PENDING', 'REVIEWED', 'SHORTLISTED', 'INTERVIEW', 'OFFER', 'REJECTED']
        
        for job in jobs:
            # Random number of applicants for each job
            num_applicants = random.randint(0, 8)
            applicants_for_job = random.sample(seekers, num_applicants)
            
            views_count = 0
            
            for applicant in applicants_for_job:
                Application.objects.create(
                    job=job,
                    applicant=applicant,
                    cover_letter="I am very interested in this position and believe I am a great fit.",
                    status=random.choice(status_choices),
                    applied_at=timezone.now() - timedelta(days=random.randint(0, 10))
                )
                JobEngagement.objects.create(job=job, user=applicant, action_type='VIEW')
                JobEngagement.objects.create(job=job, user=applicant, action_type='CLICK')
                views_count += 1
                
            # Random extra views
            extra_views = random.randint(5, 25)
            for _ in range(extra_views):
                viewer = random.choice([random.choice(seekers), None])
                JobEngagement.objects.create(job=job, user=viewer, action_type='VIEW')
                if random.random() > 0.7:
                    JobEngagement.objects.create(job=job, user=viewer, action_type='CLICK')
                views_count += 1
                
            Job.objects.filter(id=job.id).update(views_count=views_count)
            
        self.stdout.write("Created job applications and analytics data.")

        # 5. Create Blog Data
        categories = ["Tech Trends", "Career Advice", "Company News", "Interviews"]
        cat_objs = []
        for c in categories:
            cat, _ = Category.objects.get_or_create(name=c, slug=c.lower().replace(" ", "-"))
            cat_objs.append(cat)
            
        for i in range(10):
            Post.objects.create(
                title=f"Blog Post Title {i}",
                slug=f"blog-post-title-{i}",
                author=random.choice(employers), # Using employer as author for simplicity
                category=random.choice(cat_objs),
                content="This is a fantastic blog post about industry insights and career growth...",
                status='published',
                created_at=timezone.now() - timedelta(days=random.randint(0, 60))
            )
        self.stdout.write("Created blog posts.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
