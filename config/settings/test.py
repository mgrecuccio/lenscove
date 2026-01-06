from .base import *
import os

DEBUG = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is required in production")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Contact email settings
DEFAULT_FROM_EMAIL = "no-reply@lenscove.com"
CONTACT_RECEIVER_EMAIL = "admin@lenscove.com"

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "tmp/emails"
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'marco.grecuccio@mgrtech.eu'
# EMAIL_HOST_PASSWORD = 'yourpassword'
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