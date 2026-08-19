import os
import django
import sys

def clear_django_cache():
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobbee.settings')
    
    try:
        # Initialize Django
        django.setup()
        
        # Import cache after setup
        from django.core.cache import cache
        
        print("Clearing cache...")
        cache.clear()
        print("Cache cleared successfully!")
        
    except Exception as e:
        print(f"Error clearing cache: {e}")
        sys.exit(1)

if __name__ == '__main__':
    clear_django_cache()
