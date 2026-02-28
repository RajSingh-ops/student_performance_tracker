from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    load_dotenv(str(BASE_DIR / ".env"))
except:
    pass

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "demo"),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only"
)

DEBUG = True
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,build2026.onrender.com,testserver,dishes-bone-triumph-agreements.trycloudflare.com"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://build2026.onrender.com",
    "https://dishes-bone-triumph-agreements.trycloudflare.com",
]

INSTALLED_APPS = [
    "tracker.apps.TrackerConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "cloudinary",
    "cloudinary_storage",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "yearscore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'tracker.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = "yearscore.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DATABASE_URL"):
    import dj_database_url
    DATABASES["default"] = dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"



CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "demo")  # Fallback to "demo" for local dev
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
}

if CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")