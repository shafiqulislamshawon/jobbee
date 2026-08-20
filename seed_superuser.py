import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "codewithshawon"
email = "codewithshawon@gmail.com"
password = "1110215820"

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    print(f"Superuser {username} already exists.")
