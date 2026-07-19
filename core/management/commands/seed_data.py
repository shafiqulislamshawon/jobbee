import random
import uuid
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from accounts.models import (
    User, EmployerProfile, SeekerProfile, Education, Experience,
    Certification, CompanyPhoto, CompanyReview, Referral, RecruiterSeat, Notification
)
from jobs.models import (
    JobCategory, Job, Application, SavedCandidate, JobEngagement,
    SavedSearch, Assessment, AssessmentResult
)
from blog.models import Category, Post
from subscriptions.models import Plan, EmployerSubscription, Transaction, AddOn, EmployerAddOn, AdSpace, AdBooking
from core.models import HeroSectionSettings, TrustedCompany

class Command(BaseCommand):
    help = 'Seeds clean, highly realistic, rich data for Jobbee manual testing'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old seed data...")

        # Delete all existing data in reverse order of foreign keys
        Notification.objects.all().delete()
        Referral.objects.all().delete()
        RecruiterSeat.objects.all().delete()
        CompanyReview.objects.all().delete()
        CompanyPhoto.objects.all().delete()
        Certification.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        
        SavedCandidate.objects.all().delete()
        SavedSearch.objects.all().delete()
        JobEngagement.objects.all().delete()
        AssessmentResult.objects.all().delete()
        Assessment.objects.all().delete()
        Application.objects.all().delete()
        Job.objects.all().delete()
        JobCategory.objects.all().delete()
        
        AdBooking.objects.all().delete()
        AdSpace.objects.all().delete()
        Transaction.objects.all().delete()
        EmployerSubscription.objects.all().delete()
        EmployerAddOn.objects.all().delete()
        AddOn.objects.all().delete()
        Plan.objects.all().delete()
        
        Post.objects.all().delete()
        Category.objects.all().delete()
        
        EmployerProfile.objects.all().delete()
        SeekerProfile.objects.all().delete()
        
        # Clear all users except maybe actual superusers if desired, but we'll recreate a clean set
        User.objects.all().delete()

        self.stdout.write("Old data deleted successfully.")

        # Set up dummy files for ImageField and FileField uploads
        # Tiny 1x1 transparent GIF
        gif_data = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        logo_file = SimpleUploadedFile("logo.gif", gif_data, content_type="image/gif")
        banner_file = SimpleUploadedFile("banner.gif", gif_data, content_type="image/gif")
        photo_file = SimpleUploadedFile("photo.gif", gif_data, content_type="image/gif")
        blog_file = SimpleUploadedFile("blog.gif", gif_data, content_type="image/gif")
        ad_file = SimpleUploadedFile("ad.gif", gif_data, content_type="image/gif")
        
        # Simple text pdf content
        pdf_data = b"%PDF-1.4\n%...\n%%EOF"
        resume_file = SimpleUploadedFile("resume.pdf", pdf_data, content_type="application/pdf")

        # 1. Create Base Superuser
        self.stdout.write("Creating superuser admin/admin123...")
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        # 2. Hero Settings & Trusted Companies
        self.stdout.write("Creating Hero & Home page settings...")
        HeroSectionSettings.objects.all().delete()
        HeroSectionSettings.objects.create(
            badge_text="Version 2.0 Live - Fast & Premium Hiring",
            heading_line_1="Connect with your",
            heading_line_2_colored="dream company.",
            subheading="The ultra-fast, premium hiring infrastructure designed for top-tier software engineers, UI/UX designers, product managers, and creative professionals.",
            popular_tags="Remote, Python, Django, React, Design, Product, Barista",
            card_1_number="12,400+",
            card_1_label="Active Postings",
            card_2_title="Senior Python Architect",
            card_2_tag_1="FULL TIME",
            card_2_tag_2="REMOTE",
            card_3_number="4.8/5",
            card_3_label="Seeker Satisfaction",
            card_4_number="18h",
            card_4_label="Avg. Time-to-Interview"
        )
        
        TrustedCompany.objects.all().delete()
        for i, name in enumerate(["Google", "Microsoft", "Stripe", "Vercel", "Netflix"]):
            TrustedCompany.objects.create(
                name=name,
                logo=logo_file,
                order=i
            )

        # 3. Create Subscription Plans (Starter, Business, Enterprise)
        self.stdout.write("Creating Subscription Plans...")
        plan_starter = Plan.objects.create(
            name="Starter",
            price=1999.00,
            job_limit=1,
            duration_days=30,
            best_for="Small businesses & startups",
            job_posts_text="1 Active Job (30 Days)",
            applications_text="Unlimited",
            cv_database_access="Applicants Only",
            featured_jobs_text="—",
            homepage_placement=False,
            social_media_promotion="—",
            company_branding="Logo + Basic Company Profile",
            analytics_dashboard="Basic",
            dedicated_account_manager=False,
            recruitment_consultation=False,
            priority_customer_support="Email",
            remote_hybrid_support=False,
            custom_hiring_campaigns=False,
        )
        plan_business = Plan.objects.create(
            name="Business",
            price=9999.00,
            job_limit=10,
            duration_days=180,
            best_for="Growing companies & HR teams",
            job_posts_text="Up to 10 Active Jobs (30 days)",
            applications_text="Unlimited",
            cv_database_access="Full Applicant Access",
            featured_jobs_text="3 Featured Jobs",
            homepage_placement=True,
            social_media_promotion="2 Campaigns / Month",
            company_branding="Logo + Company Banner",
            analytics_dashboard="Advanced Reports",
            dedicated_account_manager=False,
            recruitment_consultation=True,
            priority_customer_support="Priority WhatsApp & Email",
            remote_hybrid_support=True,
            custom_hiring_campaigns=False,
        )
        plan_enterprise = Plan.objects.create(
            name="Enterprise",
            price=24999.00,
            job_limit=30,
            duration_days=365,
            best_for="Large companies & recruitment agencies",
            job_posts_text="*Unlimited Job Posts (up to 30 jobs)",
            applications_text="Unlimited",
            cv_database_access="Premium CV Database Access",
            featured_jobs_text="Unlimited Featured Jobs",
            homepage_placement=True,
            social_media_promotion="Unlimited Campaigns",
            company_branding="Premium Employer Branding",
            analytics_dashboard="Custom Analytics & Insights",
            dedicated_account_manager=True,
            recruitment_consultation=True,
            priority_customer_support="Dedicated Phone + WhatsApp",
            remote_hybrid_support=True,
            custom_hiring_campaigns=True,
        )
        plans = [plan_starter, plan_business, plan_enterprise]

        # 4. Create AddOns
        self.stdout.write("Creating AddOns...")
        addons_data = [
            {'name': 'Featured Job (10 Days)', 'price': 999.00, 'addon_type': 'FEATURED_JOB', 'description': 'Make your job stand out in search results for 10 days.'},
            {'name': 'Extra Starter Job Post', 'price': 500.00, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Starter plan.'},
            {'name': 'Extra Business Job Post', 'price': 1000.00, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Business plan.'},
            {'name': 'Extra Enterprise Job Post', 'price': 1500.00, 'addon_type': 'EXTRA_JOB', 'description': 'Post 1 additional job on your Enterprise plan.'},
            {'name': 'Homepage Banner', 'price': 2999.00, 'addon_type': 'BANNER', 'description': 'Display your company banner prominently on the homepage.'},
            {'name': 'Facebook Promotion', 'price': 1499.00, 'addon_type': 'SOCIAL_PROMO', 'description': 'We will promote your job on our Facebook page.'},
            {'name': 'LinkedIn Promotion', 'price': 1999.00, 'addon_type': 'SOCIAL_PROMO', 'description': 'We will promote your job on our LinkedIn network.'},
            {'name': 'CV Database Access (100 CVs)', 'price': 2499.00, 'addon_type': 'CV_DB', 'description': 'Unlock contact information for 100 candidates from our CV database.'},
            {'name': 'Candidate Shortlisting Service', 'price': 4999.00, 'addon_type': 'SHORTLISTING', 'description': 'Let our expert recruiters shortlist the best candidates for you.'},
            {'name': 'Employer Verification Badge', 'price': 999.00, 'addon_type': 'VERIFICATION', 'description': 'Instantly get the verified badge next to your company name.'},
        ]
        created_addons = []
        for data in addons_data:
            addon, _ = AddOn.objects.get_or_create(name=data['name'], defaults=data)
            created_addons.append(addon)

        # 5. Create AdSpaces
        self.stdout.write("Creating AdSpaces...")
        adspace_top = AdSpace.objects.create(
            name="Homepage Leaderboard",
            identifier="homepage_top",
            width=728,
            height=90,
            price_per_day=150.00,
            description="Premium banner slot at the top of the home page"
        )
        adspace_sidebar = AdSpace.objects.create(
            name="Sidebar Promo Rectangle",
            identifier="sidebar_rect",
            width=300,
            height=250,
            price_per_day=75.00,
            description="Sidebar slot on the job search results page"
        )

        # 6. Create Job Categories
        self.stdout.write("Creating Job Categories...")
        categories_list = [
            ("IT & Software", "it-software", "fa-code"),
            ("Design & Creative", "design-creative", "fa-palette"),
            ("Marketing & Sales", "marketing-sales", "fa-bullhorn"),
            ("Product Management", "product-management", "fa-tasks"),
            ("Customer Support", "customer-support", "fa-headset"),
            ("Restaurant & Hospitality", "restaurant-hospitality", "fa-utensils"),
            ("Finance & Accounting", "finance-accounting", "fa-calculator")
        ]
        job_categories = {}
        for name, slug, icon in categories_list:
            cat = JobCategory.objects.create(name=name, slug=slug, icon=icon)
            job_categories[name] = cat

        # 7. Create Employers (5 realistic profiles)
        self.stdout.write("Creating Employers...")
        pw = make_password("password123")
        
        employers_data = [
            {
                "username": "google_emp",
                "email": "hiring@google.com",
                "company_name": "Google LLC",
                "industry": "Tech & Search",
                "company_size": "500+",
                "is_verified": True,
                "website": "https://careers.google.com",
                "description": "Google's mission is to organize the world's information and make it universally accessible and useful. Join our engineering, design, and product groups to build the future.",
                "plan": plan_enterprise,
                "credits": 100
            },
            {
                "username": "stripe_emp",
                "email": "careers@stripe.com",
                "company_name": "Stripe Inc.",
                "industry": "Fintech & Payments",
                "company_size": "201-500",
                "is_verified": True,
                "website": "https://stripe.com/jobs",
                "description": "Stripe is a financial infrastructure platform for the internet. Millions of businesses—from the world's largest enterprises to new startups—use Stripe to accept payments and manage operations.",
                "plan": plan_business,
                "credits": 20
            },
            {
                "username": "vercel_emp",
                "email": "jobs@vercel.com",
                "company_name": "Vercel",
                "industry": "Cloud Infrastructure",
                "company_size": "51-200",
                "is_verified": True,
                "website": "https://vercel.com/careers",
                "description": "Vercel provides the developer experience and infrastructure to build, deploy, and scale the frontend web. We are creators of Next.js.",
                "plan": plan_business,
                "credits": 15
            },
            {
                "username": "starbucks_emp",
                "email": "storejobs@starbucks.com",
                "company_name": "Starbucks Coffee",
                "industry": "Food & Beverage",
                "company_size": "500+",
                "is_verified": False,
                "website": "https://starbucks.com/careers",
                "description": "To inspire and nurture the human spirit – one person, one cup and one neighborhood at a time. We offer competitive benefits and growth paths.",
                "plan": plan_starter,
                "credits": 2
            },
            {
                "username": "sweet_treats",
                "email": "jobs@sweettreatsbakery.com",
                "company_name": "Sweet Treats Local Bakery",
                "industry": "Retail & Food",
                "company_size": "1-10",
                "is_verified": False,
                "website": "https://sweettreatsbakery.com",
                "description": "A beloved family-owned local bakery serving fresh pastries, customized wedding cakes, and artisanal breads to our community since 2012.",
                "plan": plan_starter,
                "credits": 0
            }
        ]

        employers = []
        for emp_info in employers_data:
            user = User.objects.create(
                username=emp_info["username"],
                email=emp_info["email"],
                password=pw,
                is_employer=True
            )
            profile = EmployerProfile.objects.create(
                user=user,
                company_name=emp_info["company_name"],
                industry=emp_info["industry"],
                company_size=emp_info["company_size"],
                is_verified=emp_info["is_verified"],
                website=emp_info["website"],
                description=emp_info["description"],
                logo=logo_file,
                company_banner=banner_file,
                verification_status="APPROVED" if emp_info["is_verified"] else "PENDING",
                credits=emp_info["credits"]
            )
            employers.append(profile)
            
            # Setup active subscription
            start_dt = timezone.now() - timedelta(days=5)
            end_dt = start_dt + timedelta(days=emp_info["plan"].duration_days)
            EmployerSubscription.objects.create(
                employer=profile,
                plan=emp_info["plan"],
                start_date=start_dt,
                end_date=end_dt,
                status="ACTIVE"
            )
            
            # Create a couple of transactions
            Transaction.objects.create(
                subscription=profile.subscription,
                amount=emp_info["plan"].price,
                payment_method="Stripe Credit Card",
                transaction_id=f"ch_{uuid.uuid4().hex[:12]}",
                status="COMPLETED"
            )
            
            # Create some company photos
            CompanyPhoto.objects.create(
                employer=profile,
                image=photo_file,
                caption="Our beautiful modern office space"
            )

        # 8. Create Seekers (8 realistic profiles)
        self.stdout.write("Creating Seekers...")
        seekers_data = [
            {
                "username": "alice_dev",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@example.com",
                "skills": "Python, Django, PostgreSQL, Docker, AWS, Git",
                "gender": "F",
                "age_group": "25-34",
                "location": "US",
                "portfolio_url": "https://alicej-portfolio.dev",
                "education": [
                    {"institution": "Stanford University", "degree": "B.S. Computer Science", "field_of_study": "Systems & Web Dev", "start_year": 2016, "end_year": 2020}
                ],
                "experience": [
                    {"job_title": "Software Engineer II", "company": "GitHub Inc.", "start_year": 2021, "end_year": 2024, "desc": "Developed API features using Ruby on Rails and Python. Maintained high-performance database queries."}
                ],
                "certifications": [
                    {"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "year": 2023}
                ]
            },
            {
                "username": "bob_frontend",
                "first_name": "Bob",
                "last_name": "Smith",
                "email": "bob.smith@example.com",
                "skills": "React, TypeScript, Next.js, HTML5, CSS3, TailwindCSS",
                "gender": "M",
                "age_group": "25-34",
                "location": "GB",
                "portfolio_url": "https://bobsmith.codes",
                "education": [
                    {"institution": "University College London", "degree": "M.S. Software Engineering", "field_of_study": "Software Engineering", "start_year": 2018, "end_year": 2019}
                ],
                "experience": [
                    {"job_title": "Frontend Engineer", "company": "Monzo Bank", "start_year": 2020, "end_year": 2025, "desc": "Built and optimized client-facing web applications using React and TypeScript. Improved accessibility score by 35%."}
                ],
                "certifications": []
            },
            {
                "username": "charlie_designer",
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie.design@example.com",
                "skills": "UI/UX, Figma, Adobe XD, User Research, Prototyping, Wireframing",
                "gender": "O",
                "age_group": "18-24",
                "location": "CA",
                "portfolio_url": "https://dribbble.com/charlieb",
                "education": [
                    {"institution": "Emily Carr University of Art + Design", "degree": "Bachelor of Design", "field_of_study": "Interaction Design", "start_year": 2019, "end_year": 2023}
                ],
                "experience": [
                    {"job_title": "Junior UX Designer", "company": "Shopify", "start_year": 2023, "end_year": 2025, "desc": "Created low and high fidelity mockups. Conducted weekly user research sessions with 15+ merchants."}
                ],
                "certifications": []
            },
            {
                "username": "diana_marketing",
                "first_name": "Diana",
                "last_name": "Prince",
                "email": "diana.prince@example.com",
                "skills": "SEO, Content Marketing, Social Media Strategy, Google Analytics, Copywriting",
                "gender": "F",
                "age_group": "35-44",
                "location": "DE",
                "portfolio_url": "https://dianaprincemarketing.de",
                "education": [
                    {"institution": "LMU Munich", "degree": "B.A. Communication & Media", "field_of_study": "Public Relations", "start_year": 2012, "end_year": 2016}
                ],
                "experience": [
                    {"job_title": "Digital Marketing Specialist", "company": "Zalando SE", "start_year": 2017, "end_year": 2024, "desc": "Managed global social media profiles with over 2M combined followers. Led campaigns yielding 15% YoY growth."}
                ],
                "certifications": [
                    {"name": "Google Analytics Individual Qualification", "issuer": "Google", "year": 2022}
                ]
            },
            {
                "username": "evan_pm",
                "first_name": "Evan",
                "last_name": "Wright",
                "email": "evan.wright@example.com",
                "skills": "Product Strategy, Agile, Scrum, Product Roadmaps, JIRA, SQL",
                "gender": "M",
                "age_group": "25-34",
                "location": "AU",
                "portfolio_url": "",
                "education": [
                    {"institution": "University of Sydney", "degree": "B.S. Business Information Systems", "field_of_study": "Information Systems", "start_year": 2014, "end_year": 2018}
                ],
                "experience": [
                    {"job_title": "Product Owner", "company": "Atlassian", "start_year": 2019, "end_year": 2024, "desc": "Product owner for the Jira integrations team. Collaborated with 3 cross-functional teams to launch 10+ ecosystem integrations."}
                ],
                "certifications": [
                    {"name": "Certified Scrum Product Owner (CSPO)", "issuer": "Scrum Alliance", "year": 2020}
                ]
            },
            {
                "username": "fiona_sales",
                "first_name": "Fiona",
                "last_name": "Gallagher",
                "email": "fiona.g@example.com",
                "skills": "Enterprise Sales, Account Management, Cold Calling, Negotiating, Salesforce",
                "gender": "F",
                "age_group": "25-34",
                "location": "IN",
                "portfolio_url": "",
                "education": [
                    {"institution": "Delhi University", "degree": "B.Com Honors", "field_of_study": "Business", "start_year": 2015, "end_year": 2018}
                ],
                "experience": [
                    {"job_title": "Sales Account Executive", "company": "HubSpot", "start_year": 2019, "end_year": 2025, "desc": "Exceeded annual sales quota by 120% consistently. Handled mid-market enterprise accounts across South Asia."}
                ],
                "certifications": []
            },
            {
                "username": "george_barista",
                "first_name": "George",
                "last_name": "Costanza",
                "email": "george.costanza@example.com",
                "skills": "Latte Art, Espresso Preparation, Customer Service, Cash Register, Food Safety",
                "gender": "M",
                "age_group": "35-44",
                "location": "US",
                "portfolio_url": "",
                "education": [
                    {"institution": "Queens College", "degree": "B.A. History", "field_of_study": "General History", "start_year": 2005, "end_year": 2009}
                ],
                "experience": [
                    {"job_title": "Lead Barista", "company": "Blue Bottle Coffee", "start_year": 2021, "end_year": 2024, "desc": "Maintained clean workspace, pulled high-quality espresso shots, trained 4 new staff members."}
                ],
                "certifications": [
                    {"name": "ServSafe Manager Certification", "issuer": "National Restaurant Association", "year": 2023}
                ]
            },
            {
                "username": "hannah_jr",
                "first_name": "Hannah",
                "last_name": "Abbott",
                "email": "hannah.abbott@example.com",
                "skills": "HTML, CSS, JavaScript, Bootstrap, Git, Python",
                "gender": "F",
                "age_group": "18-24",
                "location": "GB",
                "portfolio_url": "https://hannahabbott-portfolio.netlify.app",
                "education": [
                    {"institution": "University of Birmingham", "degree": "B.S. Computer Science", "field_of_study": "Computer Science", "start_year": 2021, "end_year": 2024}
                ],
                "experience": [],
                "certifications": []
            }
        ]

        seekers = []
        for seeker_info in seekers_data:
            user = User.objects.create(
                username=seeker_info["username"],
                first_name=seeker_info["first_name"],
                last_name=seeker_info["last_name"],
                email=seeker_info["email"],
                password=pw,
                is_seeker=True
            )
            seeker_profile = SeekerProfile.objects.create(
                user=user,
                resume=resume_file,
                portfolio_url=seeker_info["portfolio_url"],
                skills=seeker_info["skills"],
                gender=seeker_info["gender"],
                age_group=seeker_info["age_group"],
                location=seeker_info["location"],
                resume_score=85,
                missing_skills="Kubernetes, Go, GraphQL" if "Python" in seeker_info["skills"] else "None",
                resume_suggestions="Add more quantified metrics to your bullet points to illustrate your achievements."
            )
            seekers.append(seeker_profile)

            # Add education
            for edu_info in seeker_info["education"]:
                Education.objects.create(
                    seeker=seeker_profile,
                    institution=edu_info["institution"],
                    degree=edu_info["degree"],
                    field_of_study=edu_info["field_of_study"],
                    start_date=date(edu_info["start_year"], 9, 1),
                    end_date=date(edu_info["end_year"], 6, 1) if edu_info["end_year"] else None
                )

            # Add experience
            for exp_info in seeker_info["experience"]:
                Experience.objects.create(
                    seeker=seeker_profile,
                    job_title=exp_info["job_title"],
                    company=exp_info["company"],
                    start_date=date(exp_info["start_year"], 1, 1),
                    end_date=date(exp_info["end_year"], 12, 31) if exp_info["end_year"] else None,
                    is_current=(exp_info["end_year"] is None),
                    description=exp_info["desc"]
                )

            # Add certifications
            for cert_info in seeker_info["certifications"]:
                Certification.objects.create(
                    seeker=seeker_profile,
                    name=cert_info["name"],
                    issuer=cert_info["issuer"],
                    issue_date=date(cert_info["year"], 5, 1)
                )

        # 9. Create Jobs (highly realistic descriptions and parameters)
        self.stdout.write("Creating Jobs...")
        jobs_data = [
            {
                "employer": "google_emp",
                "category": "IT & Software",
                "title": "Senior Staff Software Engineer (Python Core)",
                "description": "<p>Google is seeking a Senior Staff Python Developer to join our Cloud Infrastructure team. You will lead design decisions for core automation platforms used by millions of instances worldwide.</p>",
                "responsibilities": "Design and build core backend architectures in Python.\nOptimize high-throughput infrastructure components.\nLead teams, review code, and provide technical guidance.",
                "requirements": "7+ years of experience with Python/Django/Go in production.\nExcellent knowledge of cloud systems (GCP/AWS) and distributed architectures.\nB.S. or M.S. in Computer Science or related fields.",
                "currency": "USD",
                "salary_min": 180000,
                "salary_max": 240000,
                "employment_type": "FULL_TIME",
                "remote_status": "HYBRID",
                "location": "US",
                "skills": "Python, Django, GCP, Kubernetes, Distributed Systems",
                "experience": "7+ Years",
                "education": "BS or MS in Computer Science",
                "is_featured": True
            },
            {
                "employer": "google_emp",
                "category": "Product Management",
                "title": "Lead Product Manager - Google Maps Platform",
                "description": "<p>Work on the product direction for the maps platform API, collaborating with developer communities globally to launch new routing algorithms and monetization streams.</p>",
                "responsibilities": "Define product roadmap and strategy.\nCoordinate engineering, design, and developer relations.\nDefine and track success metrics for features.",
                "requirements": "5+ years in technical product management.\nExperience with developer-facing API products.\nExcellent presentation and leadership capabilities.",
                "currency": "USD",
                "salary_min": 160000,
                "salary_max": 210000,
                "employment_type": "FULL_TIME",
                "remote_status": "ON_SITE",
                "location": "US",
                "skills": "Product Strategy, APIs, Data Analytics, Agile",
                "experience": "5+ Years",
                "education": "Bachelor's Degree",
                "is_featured": False
            },
            {
                "employer": "stripe_emp",
                "category": "IT & Software",
                "title": "Backend Software Engineer (Payments Core)",
                "description": "<p>Stripe is looking for a backend engineer to design scalable API systems handling payment flows. You will work on robustness, reliability, and security of critical financial channels.</p>",
                "responsibilities": "Build scalable, highly reliable backend microservices.\nInterface with bank integrations and processing partners.\nRefactor legacy modules to minimize latency.",
                "requirements": "4+ years of industry experience.\nHigh proficiency in Python, Go, or Ruby.\nStrong foundation in database systems and REST APIs.",
                "currency": "USD",
                "salary_min": 140000,
                "salary_max": 195000,
                "employment_type": "FULL_TIME",
                "remote_status": "REMOTE",
                "location": "US",
                "skills": "Python, Go, PostgreSQL, REST APIs, Security",
                "experience": "4+ Years",
                "education": "No Degree Required",
                "is_featured": True
            },
            {
                "employer": "stripe_emp",
                "category": "Design & Creative",
                "title": "Senior UI/UX Designer - Checkout Experience",
                "description": "<p>Shape the checkout experience used by millions of merchants worldwide. Conduct research and build interactive prototypes that maximize payment conversion rates.</p>",
                "responsibilities": "Design intuitive UI components for the Stripe Checkout platform.\nPerform user studies and analyze heatmaps.\nDeliver high fidelity mockup assets to engineering team.",
                "requirements": "5+ years of UX design experience with a stellar web portfolio.\nExceptional Figma skills.\nStrong knowledge of web typography, conversion optimization, and design systems.",
                "currency": "GBP",
                "salary_min": 75000,
                "salary_max": 105000,
                "employment_type": "FULL_TIME",
                "remote_status": "HYBRID",
                "location": "GB",
                "skills": "UI/UX, Figma, Conversion Optimization, Prototyping",
                "experience": "5+ Years",
                "education": "Design Degree or Equivalent Portfolio",
                "is_featured": False
            },
            {
                "employer": "stripe_emp",
                "category": "Marketing & Sales",
                "title": "Strategic Account Executive",
                "description": "<p>Grow our mid-market sales. You will work with fast-growing startups to integrate Stripe payment infrastructure and treasury products.</p>",
                "responsibilities": "Own the complete sales cycle from prospecting to closing.\nDraft custom quotes and contract modifications.\nCoordinate developer integration calls.",
                "requirements": "3+ years in enterprise B2B SaaS sales.\nFamiliarity with billing and payment integrations.\nExcellent communication skills.",
                "currency": "CAD",
                "salary_min": 90000,
                "salary_max": 130000,
                "employment_type": "FULL_TIME",
                "remote_status": "HYBRID",
                "location": "CA",
                "skills": "SaaS Sales, Account Management, CRM, Negotiation",
                "experience": "3+ Years",
                "education": "Bachelor's Degree",
                "is_featured": False
            },
            {
                "employer": "vercel_emp",
                "category": "IT & Software",
                "title": "Core Next.js Developer",
                "description": "<p>Work directly on Next.js core, improving hot module reloading speed, routing stability, and hydration optimizations. Collaborate with open-source contributors.</p>",
                "responsibilities": "Submit pull requests to Next.js core repository.\nImplement RFC suggestions from the community.\nOptimize compiler builds (Turbopack).",
                "requirements": "Deep understanding of React internals, bundling tools, and Webpack/Rspack/Turbopack.\nContributions to major open-source web frameworks.\nExcellent JavaScript/TypeScript skill.",
                "currency": "USD",
                "salary_min": 150000,
                "salary_max": 200000,
                "employment_type": "FULL_TIME",
                "remote_status": "REMOTE",
                "location": "US",
                "skills": "React, Next.js, Webpack, Rust, TypeScript",
                "experience": "5+ Years",
                "education": "Not Required",
                "is_featured": True
            },
            {
                "employer": "vercel_emp",
                "category": "Customer Support",
                "title": "Developer Support Engineer",
                "description": "<p>Help Vercel customers resolve deployment errors, custom domain misconfigurations, and serverless function cold-starts. High technical debugging role.</p>",
                "responsibilities": "Respond to enterprise customer tickets with code solutions.\nWrite documentation for troubleshooting steps.\nCoordinate with core engineers to report platform bugs.",
                "requirements": "Excellent debugging skills of Next.js, Node.js, and general web applications.\nGreat written English.\nFamiliarity with DNS and CDN concepts.",
                "currency": "EUR",
                "salary_min": 50000,
                "salary_max": 75000,
                "employment_type": "FULL_TIME",
                "remote_status": "REMOTE",
                "location": "DE",
                "skills": "Node.js, DNS, Debugging, Next.js, Customer Service",
                "experience": "2+ Years",
                "education": "Technical Diploma or Experience",
                "is_featured": False
            },
            {
                "employer": "starbucks_emp",
                "category": "Restaurant & Hospitality",
                "title": "Store Shift Supervisor",
                "description": "<p>Starbucks is seeking a Shift Supervisor to run store operations, manage cash boxes, assign barista shifts, and maintain food safety guidelines.</p>",
                "responsibilities": "Supervise store employees during shifts.\nPrepare handovers and run cashier reconciliation.\nNurture customer experience and resolve complaints.",
                "requirements": "1+ year experience in retail or hospitality supervision.\nAbility to work flexible early morning or weekend hours.\nStrong communication skills.",
                "currency": "USD",
                "salary_min": 35000,
                "salary_max": 45000,
                "employment_type": "FULL_TIME",
                "remote_status": "ON_SITE",
                "location": "US",
                "skills": "Supervision, Food Safety, Customer Service, Cash Management",
                "experience": "1+ Year",
                "education": "High School Diploma",
                "is_featured": False
            },
            {
                "employer": "starbucks_emp",
                "category": "Restaurant & Hospitality",
                "title": "Experienced Barista (Part-Time)",
                "description": "<p>Nurture customers with perfectly brewed coffee. You will handle espresso machines, brew tea, and maintain clean counter stations.</p>",
                "responsibilities": "Craft hot and cold espresso drinks to specification.\nClean tables and wash tools.\nMaintain positive attitude under fast-paced morning rushes.",
                "requirements": "Previous experience as a barista or fast food cashier preferred but not required.\nExcellent customer-facing etiquette.\nMust be punctual.",
                "currency": "GBP",
                "salary_min": 18000,
                "salary_max": 24000,
                "employment_type": "PART_TIME",
                "remote_status": "ON_SITE",
                "location": "GB",
                "skills": "Coffee, Customer Service, Barista, Teamwork",
                "experience": "Entry Level",
                "education": "No education required",
                "is_featured": False
            },
            {
                "employer": "sweet_treats",
                "category": "Restaurant & Hospitality",
                "title": "Lead Pastry Chef & Baker",
                "description": "<p>Lead our morning baking program. Craft croissants, sourdough bread, cakes, and cookies. Requires early morning schedules.</p>",
                "responsibilities": "Bake daily inventory starting at 4:00 AM.\nDesign customized cakes for pre-orders.\nManage ingredient inventory and bakery hygiene standards.",
                "requirements": "3+ years of professional bakery experience.\nExpertise in dough fermentation and cake decorating.\nDegree in Culinary Arts or Pastry arts is a major plus.",
                "currency": "USD",
                "salary_min": 45000,
                "salary_max": 58000,
                "employment_type": "FULL_TIME",
                "remote_status": "ON_SITE",
                "location": "US",
                "skills": "Baking, Pastry, Food Preparation, Inventory Control",
                "experience": "3+ Years",
                "education": "Pastry Arts Diploma preferred",
                "is_featured": False
            }
        ]

        created_jobs = []
        for job_info in jobs_data:
            emp_user = User.objects.get(username=job_info["employer"])
            cat = job_categories[job_info["category"]]
            job = Job.objects.create(
                employer=emp_user,
                category=cat,
                title=job_info["title"],
                description=job_info["description"],
                responsibilities=job_info["responsibilities"],
                requirements=job_info["requirements"],
                currency=job_info["currency"],
                salary_min=job_info["salary_min"],
                salary_max=job_info["salary_max"],
                employment_type=job_info["employment_type"],
                remote_status=job_info["remote_status"],
                location=job_info["location"],
                skills=job_info["skills"],
                experience=job_info["experience"],
                education=job_info["education"],
                deadline=date.today() + timedelta(days=random.randint(15, 60)),
                is_active=True,
                is_featured=job_info["is_featured"],
                views_count=random.randint(10, 150)
            )
            created_jobs.append(job)

        # 10. Create Job Applications (highly realistic test scenarios)
        self.stdout.write("Creating Job Applications...")
        
        # We want to match Alice (Python developer) to Google Python and Stripe Backend roles
        # Bob (Frontend) to Stripe Checkout and Vercel Next.js roles
        # Charlie (Designer) to Stripe Senior UI/UX Designer role
        # George (Barista) to Starbucks and Sweet Treats roles
        # Hannah (Junior) to Vercel Support and Stripe Backend roles
        
        applications_scenarios = [
            {
                "username": "alice_dev",
                "job_title": "Senior Staff Software Engineer (Python Core)",
                "cover_letter": "Dear Google Team,\n\nI am thrilled to apply for the Senior Staff Software Engineer position. I have over 7 years of Python experience, most recently at GitHub, where I built and maintained core microservices that handled millions of requests. I am passionate about clean architecture and API designs.",
                "status": "SHORTLISTED",
                "score": 95
            },
            {
                "username": "alice_dev",
                "job_title": "Backend Software Engineer (Payments Core)",
                "cover_letter": "Dear Stripe Team,\n\nHaving worked heavily in financial ledgers at my previous firm, I understand the criticality of payments safety and latency. I would love to join your team to optimize core payment microservices.",
                "status": "INTERVIEW",
                "score": 92
            },
            {
                "username": "bob_frontend",
                "job_title": "Senior UI/UX Designer - Checkout Experience",
                "cover_letter": "Hi Stripe. Although my profile is primarily frontend development, I have a deep design affinity and would love to bridge the gap between design systems and code on the Checkout product.",
                "status": "REVIEWED",
                "score": 68
            },
            {
                "username": "bob_frontend",
                "job_title": "Core Next.js Developer",
                "cover_letter": "Hello Vercel team!\n\nI have been using Next.js in production for 4 years. I've read the source code of your routing packages and have previously fixed two open GitHub issues. I would be thrilled to work full time on the core Next.js project.",
                "status": "OFFER",
                "score": 98
            },
            {
                "username": "charlie_designer",
                "job_title": "Senior UI/UX Designer - Checkout Experience",
                "cover_letter": "Dear Stripe Hiring Team,\n\nI am Charlie, a UI/UX Designer. Figma is my second home. I believe Stripe sets the golden standard of web layouts, and I want to help you design the next evolution of conversion-optimized checkouts.",
                "status": "INTERVIEW",
                "score": 94
            },
            {
                "username": "george_barista",
                "job_title": "Experienced Barista (Part-Time)",
                "cover_letter": "I love coffee and make a mean latte. I am reliable, clean, and always on time.",
                "status": "OFFER",
                "score": 90
            },
            {
                "username": "george_barista",
                "job_title": "Lead Pastry Chef & Baker",
                "cover_letter": "I have experience working at coffee shops and food prep stations. Although I'm not a certified pastry chef, I learn fast.",
                "status": "REJECTED",
                "score": 45
            },
            {
                "username": "hannah_jr",
                "job_title": "Backend Software Engineer (Payments Core)",
                "cover_letter": "I recently graduated in Computer Science. I am eager to apply my Python and SQL knowledge to a real-world environment at Stripe.",
                "status": "PENDING",
                "score": 70
            },
            {
                "username": "hannah_jr",
                "job_title": "Developer Support Engineer",
                "cover_letter": "I enjoy solving coding puzzles and debugging configurations. Working at Vercel support would be a dream path for my junior career.",
                "status": "REVIEWED",
                "score": 82
            }
        ]

        for scenario in applications_scenarios:
            seeker_user = User.objects.get(username=scenario["username"])
            job = Job.objects.get(title=scenario["job_title"])
            
            Application.objects.create(
                job=job,
                applicant=seeker_user,
                cover_letter=scenario["cover_letter"],
                status=scenario["status"],
                resume=resume_file,
                match_score=scenario["score"]
            )

        # 11. Create Company Reviews
        self.stdout.write("Creating Company Reviews...")
        google_emp = EmployerProfile.objects.get(company_name="Google LLC")
        stripe_emp = EmployerProfile.objects.get(company_name="Stripe Inc.")
        
        CompanyReview.objects.create(
            employer=google_emp,
            reviewer=User.objects.get(username="alice_dev"),
            rating=5,
            title="Industry Leader with Great Culture",
            body="Outstanding engineering culture, incredible benefits, and smart peers. The scaling challenges are very real and exciting."
        )
        CompanyReview.objects.create(
            employer=stripe_emp,
            reviewer=User.objects.get(username="bob_frontend"),
            rating=4,
            title="Fast paced and developer oriented",
            body="Amazing product quality. Sometimes work hours can get long due to aggressive roadmaps, but you learn a massive amount."
        )

        # 12. Create Job Engagements (Views & Clicks metrics)
        self.stdout.write("Creating Engagement Metrics...")
        all_users = list(User.objects.all())
        for job in created_jobs:
            # Generate random views & clicks
            for _ in range(random.randint(10, 40)):
                JobEngagement.objects.create(
                    job=job,
                    user=random.choice(all_users),
                    action_type="VIEW"
                )
            for _ in range(random.randint(2, 10)):
                JobEngagement.objects.create(
                    job=job,
                    user=random.choice(all_users),
                    action_type="CLICK"
                )

        # 13. Create Saved Candidates
        self.stdout.write("Creating Saved Candidates...")
        google_user = User.objects.get(username="google_emp")
        alice_user = User.objects.get(username="alice_dev")
        SavedCandidate.objects.create(
            employer=google_user,
            seeker=alice_user,
            notes="Strong Python developer, good communicator. Fits staff criteria."
        )

        # 14. Create Saved Searches
        self.stdout.write("Creating Saved Searches...")
        SavedSearch.objects.create(
            user=alice_user,
            query="Django Remote",
            location="US"
        )

        # 15. Assessments & Results
        self.stdout.write("Creating Assessments & Results...")
        assessment_python = Assessment.objects.create(
            name="Python Fundamentals",
            description="Tests basic and intermediate Python syntax, memory management, and OOP concepts."
        )
        assessment_ux = Assessment.objects.create(
            name="UX Design Guidelines",
            description="Evaluates understanding of visual hierarchy, accessibility standards, and wireframing tools."
        )
        
        AssessmentResult.objects.create(
            seeker=User.objects.get(username="alice_dev"),
            assessment=assessment_python,
            score=96
        )
        AssessmentResult.objects.create(
            seeker=User.objects.get(username="charlie_designer"),
            assessment=assessment_ux,
            score=88
        )

        # 16. Create Ad Bookings
        self.stdout.write("Creating Ad Bookings...")
        # Stripe books homepage banner ad
        AdBooking.objects.create(
            user=User.objects.get(username="stripe_emp"),
            ad_space=adspace_top,
            image=ad_file,
            target_url="https://stripe.com/jobs",
            start_date=date.today() - timedelta(days=2),
            end_date=date.today() + timedelta(days=28),
            total_price=4500.00,
            status="APPROVED"
        )
        # Vercel books sidebar ad
        AdBooking.objects.create(
            user=User.objects.get(username="vercel_emp"),
            ad_space=adspace_sidebar,
            image=ad_file,
            target_url="https://vercel.com/careers",
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=9),
            total_price=750.00,
            status="APPROVED"
        )

        # 17. Create Referrals
        self.stdout.write("Creating Referrals...")
        Referral.objects.create(
            referrer=User.objects.get(username="alice_dev"),
            referred_email="friend.coder@gmail.com",
            status="PENDING"
        )
        Referral.objects.create(
            referrer=User.objects.get(username="alice_dev"),
            referred_email="bob.smith@example.com",
            status="REGISTERED",
            referred_user=User.objects.get(username="bob_frontend")
        )

        # 18. Create Recruiter Seats
        self.stdout.write("Creating Recruiter Seats...")
        # Add recruiter_seat to google
        google_recruiter = User.objects.create(
            username="google_recruiter_john",
            email="john.recruiter@google.com",
            password=pw,
            is_employer=True
        )
        RecruiterSeat.objects.create(
            employer_profile=google_emp,
            user=google_recruiter,
            is_active=True
        )

        # 19. Create Notifications
        self.stdout.write("Creating Notifications...")
        Notification.objects.create(
            user=alice_user,
            message="Your application for Backend Software Engineer at Stripe has been updated to Interview Scheduled!",
            link="/jobs/applications/",
            is_read=False
        )
        Notification.objects.create(
            user=User.objects.get(username="google_emp"),
            message="New application received for 'Senior Staff Software Engineer (Python Core)' from Alice Johnson.",
            link="/jobs/applications/",
            is_read=False
        )

        # 20. Seed Blog Categories & Posts
        self.stdout.write("Creating Blog posts...")
        blog_cat_career = Category.objects.create(name="Career Advice", slug="career-advice")
        blog_cat_interview = Category.objects.create(name="Interview Tips", slug="interview-tips")
        blog_cat_trends = Category.objects.create(name="Market Trends", slug="market-trends")
        
        posts_data = [
            {
                "title": "10 Things to Do Before a Job Interview",
                "content": "<p>A job interview is your opportunity to shine. Here are 10 things you must do to prepare...</p><p>1. Research the company thoroughly.</p><p>2. Practice your answers to common questions.</p><p>3. Dress for success.</p><p>You got this!</p>",
                "category": blog_cat_interview
            },
            {
                "title": "How to Negotiate Your Salary Like a Pro",
                "content": "<p>Salary negotiation can be daunting, but it's a crucial part of the hiring process.</p><p>Always know your worth before walking into the room. Use tools like Glassdoor and Payscale to research industry standards in your area.</p>",
                "category": blog_cat_career
            },
            {
                "title": "Is Remote Work Here to Stay?",
                "content": "<p>The pandemic shifted the way we work, and many companies have decided to stay fully remote.</p><p>But what does this mean for the future of commercial real estate and team culture?</p>",
                "category": blog_cat_trends
            },
            {
                "title": "The Perfect Resume Structure for 2026",
                "content": "<p>Gone are the days of objective statements. Here is how you should structure your resume this year.</p><p>Start with a strong professional summary, followed by a skills section tailored to the ATS algorithms.</p>",
                "category": blog_cat_career
            }
        ]

        for idx, item in enumerate(posts_data):
            Post.objects.create(
                title=item['title'],
                slug=slugify(item['title']),
                author=admin_user,
                content=item['content'],
                category=item['category'],
                featured_image=blog_file,
                status='PUBLISHED'
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! All clean, realistic test data generated."))
        self.stdout.write(self.style.SUCCESS(f"--------------------------------------------------"))
        self.stdout.write(self.style.SUCCESS(f"TEST ACCOUNTS CREATED (Password for all: password123):"))
        self.stdout.write(self.style.SUCCESS(f"Superuser:      username: admin      (password: admin123)"))
        self.stdout.write(self.style.SUCCESS(f"Employers:      google_emp, stripe_emp, vercel_emp, starbucks_emp, sweet_treats"))
        self.stdout.write(self.style.SUCCESS(f"Seekers:        alice_dev, bob_frontend, charlie_designer, diana_marketing, evan_pm, fiona_sales, george_barista, hannah_jr"))
        self.stdout.write(self.style.SUCCESS(f"--------------------------------------------------"))
