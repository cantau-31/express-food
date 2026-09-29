import os
from decimal import Decimal
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Définissez DJANGO_SECRET_KEY dans .env.")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
INSTALLED_APPS = ["rest_framework", "corsheaders", "common", "clients", "meals", "delivery", "orders"]
MIDDLEWARE = ["common.middleware.JsonErrorsMiddleware", "django.middleware.security.SecurityMiddleware", "corsheaders.middleware.CorsMiddleware", "django.middleware.common.CommonMiddleware"]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {}
TIME_ZONE = "Europe/Paris"
USE_TZ = True
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "common.exceptions.api_exception_handler",
}
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "express_food")
FREE_DELIVERY_THRESHOLD = Decimal(os.getenv("FREE_DELIVERY_THRESHOLD", "19.99"))
DEFAULT_DELIVERY_FEE = Decimal(os.getenv("DEFAULT_DELIVERY_FEE", "2.99"))
DEFAULT_DELIVERY_ESTIMATE = int(os.getenv("DEFAULT_DELIVERY_ESTIMATE", "20"))
if FREE_DELIVERY_THRESHOLD < 0 or DEFAULT_DELIVERY_FEE < 0 or DEFAULT_DELIVERY_ESTIMATE <= 0:
    raise ImproperlyConfigured("Configuration des frais ou estimation invalide.")
