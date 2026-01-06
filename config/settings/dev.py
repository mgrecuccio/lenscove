from .base import *
import os

DEBUG = True

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required in production")

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.ngrok-free.dev',
    'web', # docker service
]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "lenscove_dev"),
        "USER": os.getenv("POSTGRES_USER", "lenscove"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "lenscove"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),  # docker compose service name
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "tmp/emails"
DEFAULT_FROM_EMAIL = 'LensCove <marco.grecuccio@mgrtech.eu>'
CONTACT_RECEIVER_EMAIL = "admin@lenscove.com"

# Invoice settings
SHOP_NAME = os.getenv("SHOP_NAME", "LensCove Shop")
SHOP_ADDRESS = os.getenv("SHOP_ADDRESS", "123 Creative Street, Brussels, Belgium")
SHOP_EMAIL = os.getenv("SHOP_EMAIL", "support@lenscove.com")
SHOP_VAT = os.getenv("SHOP_VAT", "BE123456789")
SHOP_LOGO = os.getenv("SHOP_LOGO", "static/img/logo.png")
SHOP_PHONE = os.getenv("SHOP_PHONE", "+32 2 123 45 67")

# Email settings
BRAND_LOGO_URL = os.getenv("BRAND_LOGO_URL", "")
BRAND_BANNER_URL = os.getenv("BRAND_BANNER_URL", "")

# Mollie settings
MOLLIE_API_KEY = os.getenv("MOLLIE_API_KEY", "")
MOLLIE_REDIRECT_URL = os.getenv("MOLLIE_REDIRECT_URL", "http://localhost:8000/payment/return/")
MOLLIE_WEBHOOK_URL = os.getenv("MOLLIE_WEBHOOK_URL", "")
MOLLIE_PROFILE_ID = os.getenv("MOLLIE_PROFILE_ID", "")

# Shippo settings
SHIPPO_API_KEY = os.getenv("SHIPPO_API_KEY", "")