import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
django.setup()

from jobs.models import JobCategory

categories = [
    "Sales", "Automotive", "Construction", "Accounting", "IT & Telecommunication", 
    "Education/Training", "Restaurant", "Health Care", "Garments/Textile", 
    "Bank/ Non-Bank Fin. Institution", "Engineer/Architects", "HR/Org. Development", 
    "Data Entry/Computer Operator", "Mechanic/Technician", "Nurse", "Delivery Man", 
    "Sales Representative (SR)", "Production/Operation", "Hospitality/ Travel/ Tourism", 
    "Customer Service/Call Centre", "Marketing/Sales", "Media/Ad./Event Mgt.", 
    "Pharmaceutical", "Chef/Cook", "Agro (Plant/Animal/Fisheries)", "NGO/Development", 
    "Research/Consultancy", "Design/Creative", "Security/Support Service", "Security Guard"
]

for cat_name in categories:
    cat, created = JobCategory.objects.get_or_create(name=cat_name)
    if created:
        print(f"Created category: {cat_name}")
    else:
        print(f"Category already exists: {cat_name}")

print("Done seeding categories!")
