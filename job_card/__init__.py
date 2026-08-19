"""
job_card — Production-quality job post image generator.

Quick start:
    from job_card import generate_job_card, JobPost

    job = JobPost(
        job_id="123",
        title="Senior Software Engineer",
        company_name="TechCorp Ltd.",
        location="Dhaka, Bangladesh",
        salary="80,000 – 1,20,000 BDT",
        experience="3–5 Years",
        employment_type="Full Time",
        deadline="30 August 2026",
        skills=["Python", "Django", "PostgreSQL", "Docker"],
        description="Join our team to build scalable software used by thousands...",
        application_url="https://jobbee.com/jobs/123",
    )

    path = generate_job_card(job, template="editorial")
    print(f"Saved to: {path}")
"""
from .generator import generate_job_card, generate_all_templates, generate_job_card_from_django_job
from .models import JobPost
from .themes import BRAND_THEME, ThemeColors

__all__ = [
    'generate_job_card',
    'generate_all_templates',
    'generate_job_card_from_django_job',
    'JobPost',
    'BRAND_THEME',
    'ThemeColors',
]
