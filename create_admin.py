import os
import django

# IMPORTANT: Replace 'performance_tracker' with the name of the folder 
# that contains your settings.py file.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance_tracker.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = "admin"  # You can change this
    password = "YourSecurePassword123" # Change this!

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email='', password=password)
        print(f"SUCCESS: Superuser '{username}' created.")
    else:
        print(f"INFO: Superuser '{username}' already exists.")

if __name__ == "__main__":
    create_superuser()