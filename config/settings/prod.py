from .base import *
import os

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required in production")

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS is required in production")

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# --- Database ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "lenscove_dev"),
        "USER": os.getenv("POSTGRES_USER", "lenscove"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "lenscove"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

# --- Static & Media (WhiteNoise) ---
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

WHITENOISE_AUTOREFRESH = False
WHITENOISE_USE_FINDERS = False

SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "same-origin"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Email (file backend for now) ---
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.getenv("EMAIL_FILE_PATH", "/tmp/emails")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "LensCove <no-reply@lenscove.com>"
)
CONTACT_RECEIVER_EMAIL = os.getenv(
    "CONTACT_RECEIVER_EMAIL", "admin@lenscove.com"
)

DEFAULT_FROM_EMAIL = 'LensCove <marco.grecuccio@mgrtech.eu>'

# Invoice settings
SHOP_NAME = os.getenv("SHOP_NAME", "LensCove Shop")
SHOP_ADDRESS = os.getenv("SHOP_ADDRESS", "123 Creative Street, Brussels, Belgium")
SHOP_EMAIL = os.getenv("SHOP_EMAIL", "support@lenscove.com")
SHOP_VAT = os.getenv("SHOP_VAT", "BE123456789")
SHOP_LOGO = os.getenv("SHOP_LOGO", "static/img/logo.png")
SHOP_PHONE = os.getenv("SHOP_PHONE", "+32 2 123 45 67")

# Mollie settings
MOLLIE_API_KEY = os.getenv("MOLLIE_API_KEY", "")
MOLLIE_REDIRECT_URL = os.getenv("MOLLIE_REDIRECT_URL", "http://localhost:8000/payment/return/")
MOLLIE_WEBHOOK_URL = os.getenv("MOLLIE_WEBHOOK_URL", "")
MOLLIE_PROFILE_ID = os.getenv("MOLLIE_PROFILE_ID", "")

# Shippo settings
SHIPPO_API_KEY = os.getenv("SHIPPO_API_KEY", "")