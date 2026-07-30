import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
django.setup()

from jobs.models import JobCategory

categories = [
    "Accounting/Finance",
    "Bank/Non-Bank Fin. Institution",
    "Commercial/Supply Chain",
    "Education/Training",
    "Engineer/Architect",
    "Garments/Textile",
    "HR/Org. Development",
    "IT/Telecommunication",
    "Marketing/Sales",
    "Media/Advertisement/Event Mgt.",
    "Medical/Pharma",
    "NGO/Development",
    "Customer Support/Call Centre",
    "Design/Creative",
    "Production/Operation",
    "Hospitality/Travel/Tourism",
    "Beauty Care/Health & Fitness",
    "Electrician/Construction/Repair",
    "Secretary/Receptionist",
    "Data Entry/Operator/BPO",
    "Driving/Motor Technician",
    "Security/Support Service",
    "Law/Legal",
    "Research/Consultancy",
    "Agriculture/Plant/Animal"
]

for name in categories:
    JobCategory.objects.get_or_create(name=name)

print("Categories seeded successfully.")
