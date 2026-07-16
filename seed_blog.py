import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobbee.settings")
django.setup()

from blog.models import Category, Post
from accounts.models import User
import random

# Get or create an admin user for the author
author = User.objects.filter(is_superuser=True).first()
if not author:
    author = User.objects.first()

if not author:
    print("No users found to set as author. Please create a user first.")
    exit()

categories_data = [
    "Career Advice",
    "Interview Tips",
    "Resume Writing",
    "Employer Branding",
    "Market Trends"
]

# Create Categories
categories = []
for name in categories_data:
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={'slug': slugify(name)}
    )
    categories.append(cat)
    
posts_data = [
    {
        "title": "10 Things to Do Before a Job Interview",
        "content": "<p>A job interview is your opportunity to shine. Here are 10 things you must do to prepare...</p><p>1. Research the company thoroughly.</p><p>2. Practice your answers to common questions.</p><p>3. Dress for success.</p><p>You got this!</p>",
        "category": categories[1]
    },
    {
        "title": "How to Negotiate Your Salary Like a Pro",
        "content": "<p>Salary negotiation can be daunting, but it's a crucial part of the hiring process.</p><p>Always know your worth before walking into the room. Use tools like Glassdoor and Payscale to research industry standards in your area.</p>",
        "category": categories[0]
    },
    {
        "title": "Is Remote Work Here to Stay?",
        "content": "<p>The pandemic shifted the way we work, and many companies have decided to stay fully remote.</p><p>But what does this mean for the future of commercial real estate and team culture?</p>",
        "category": categories[4]
    },
    {
        "title": "The Perfect Resume Structure for 2026",
        "content": "<p>Gone are the days of objective statements. Here is how you should structure your resume this year.</p><p>Start with a strong professional summary, followed by a skills section tailored to the ATS algorithms.</p>",
        "category": categories[2]
    },
    {
        "title": "Attracting Top Talent: A Guide for Employers",
        "content": "<p>In a competitive market, employer branding is everything.</p><p>You need to showcase your company culture, benefits, and growth opportunities to attract the best of the best.</p>",
        "category": categories[3]
    },
    {
        "title": "Common Mistakes to Avoid in Tech Interviews",
        "content": "<p>Technical interviews are tough. Avoid these common pitfalls to increase your chances of landing that developer role.</p><p>Don't jump straight into coding. Talk through your problem-solving process out loud so the interviewer understands your logic.</p>",
        "category": categories[1]
    },
    {
        "title": "The Rise of AI in the Hiring Process",
        "content": "<p>Artificial Intelligence is changing recruitment. From automated resume screening to AI-driven chatbots for initial interviews.</p><p>Here is what candidates need to know to beat the bots.</p>",
        "category": categories[4]
    },
    {
        "title": "Why Soft Skills Matter More Than Ever",
        "content": "<p>Hard skills get you the interview, but soft skills get you the job.</p><p>Communication, adaptability, and teamwork are heavily prioritized by recruiters today.</p>",
        "category": categories[0]
    }
]

# Delete old dummy posts
Post.objects.all().delete()

# Create Posts
for item in posts_data:
    Post.objects.create(
        title=item['title'],
        slug=slugify(item['title']),
        author=author,
        content=item['content'],
        category=item['category'],
        status='PUBLISHED'
    )

print(f"Successfully seeded {len(categories)} categories and {len(posts_data)} published blog posts!")
