# LensCove

LensCove is a Django web application for browsing, ordering and customizing fine‑art prints of images. Customers can choose image dimensions, frame type and color, add items to a cart, checkout, and receive an email (HTML + plain text) with a PDF invoice attached.

---

## Tech stack / versions

- Python: 3.13
- Django: 5.2.6
- Other dependencies: see `requirements.txt`

(These versions are taken from `requirements.txt`; adjust your Python interpreter to match.)

---

## Key pages

- Home — featured and best sellers
- Gallery — browse collections and product list
- Product detail — view image, choose dimensions / frame options and add to cart
- Cart — review items, update quantity, remove items
- Checkout (Order Create) — enter shipping / contact info and place order
- Online payment — make payment with Mollie
- Order created / confirmation — order summary, invoice download
- Admin — manage products, categories, orders

---

## Main features

- Browse curated image gallery and product pages.
- Order fine art prints:
  - Choose image dimension (e.g. 10x15 / 13x18 / 20x30 or custom options).
  - Choose frame type (plastic / wood / classic / modern).
  - Choose frame color (black / white / gold / wooden).
  - Quantity selector with client-side controls.
- Cart with add / update / remove behavior.
- Checkout creates Order and OrderItem records, stores chosen options on items.
- Pay the invoice with Mollie.
- Email notifications:
  - Sends multipart email (plain text + HTML) to customer.
  - Attaches generated PDF invoice.
- PDF invoice generation using ReportLab.
- Unit tests for views, utilities and invoice generation.
- Bootstrap-based UI (Cerulean theme recommended).

---

## Project structure (high level)

- store/ — product and category models, gallery and product views
- cart/ — cart logic, add/update/remove views, forms
- orders/ — order models, forms, views, invoice generator and email utils
- payments/ — create a Mollie payment linked to the orders, redirect the customer to Mollie’s hosted checkout and handle Mollie’s webhook and update the order’s status
- templates/ — HTML and email templates (text + HTML)
- static/ — CSS/JS/assets
- config/ — project settings / URLs

---

## Setup (macOS)

1. Clone repository
   ```
   git clone https://github.com/mgrecuccio/lenscove.git
   cd lenscove
   ```

2. Create and activate virtual environment (macOS)
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Configure local settings
   - Copy or create `config/.env` or set environment variables for:
     - DJANGO_SETTINGS_MODULE (if needed for tests/tools)
     - EMAIL backend / credentials (e.g. for SMTP) and `DEFAULT_FROM_EMAIL`
     - MEDIA_ROOT and MEDIA_URL for uploaded images
   - For local development you can use the console or file email backend:
     ```
     EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
     EMAIL_FILE_PATH = BASE_DIR / 'tmp/emails'
     DEFAULT_FROM_EMAIL = 'webmaster@localhost'
     ```

5. Apply migrations and create admin user
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run development server
   ```
   python manage.py runserver
   ```
   Visit http://127.0.0.1:8000/

---

## Running tests

- Run Django tests from CLI:
  ```
  python manage.py test
  ```

- From VS Code (Test Explorer) — recommended settings (create `.vscode/settings.json`):
  ```
  {
    "python.testing.unittestEnabled": true,
    "python.testing.pytestEnabled": false,
    "python.testing.unittestArgs": [
      "-v",
      "-s",
      ".",
      "-p",
      "test_*.py"
    ],
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
  }
  ```
  - Make sure the workspace Python interpreter is set to the created venv.
  - VS Code will discover Django `TestCase` tests and allow run/debug.

---

## Notes about email & invoice tests

- The email utility sends a multipart message and attaches the generated PDF. In unit tests:
  - Use Django's `mail.outbox` to inspect sent messages.
  - Patch `orders.utils.generate_invoice` (or `orders.invoice.generate_invoice`) with `unittest.mock.patch` to avoid creating real PDF files in tests and assert it was called.
  - Example assert: `mock_generate.assert_called_once_with(order)`.
  - To assert `send_order_confirmation_email` is called from the view, patch `orders.utils.send_order_confirmation_email` in tests.

---

## Payments Gateway setup


### 1. Create a Mollie free account

1. Sign up for a Mollie account (https://www.mollie.com). Use the Dashboard to create a free test account.
2. In the Mollie Dashboard switch to "Test mode" and obtain your **Test API key** (starts with `test_...`).
3. In your local project, set the key in settings or environment variables:
   - Example (config/settings.py or env):
     - MOLLIE_API_KEY = "test_your_key_here"
     - MOLLIE_PROFILE_ID = "your_profile_id"  # optional
4. Configure redirect and webhook URLs in the Mollie dashboard (you can use ngrok during development — see below).
5. Use the test API key when running payments in development. Validate webhooks and redirect URLs with Mollie's test transactions.

Security note: never commit production API keys. Use environment variables or a secrets manager for production.

### 2. Setup ngrok to test in dev / local environment

1. Install ngrok:
   - macOS (Homebrew): `brew install --cask ngrok` or download from https://ngrok.com
2. Start your Django dev server:
   - `python manage.py runserver 8000`
3. Start ngrok to expose the local server:
   - `ngrok http 8000`
4. Copy the forward URL shown by ngrok (e.g. `https://abcd1234.ngrok.io`) and use it to configure external services:
   - Set Mollie redirect URL: `https://<ngrok-id>.ngrok.io/payments/return/`
   - Set Mollie webhook URL: `https://<ngrok-id>.ngrok.io/payments/webhook/`
   - Example settings override (use env vars in real setup):
     - MOLLIE_REDIRECT_URL = "https://abcd1234.ngrok.io/payments/return/"
     - MOLLIE_WEBHOOK_URL = "https://abcd1234.ngrok.io/payments/webhook/"
6. In general settings.py, add the ngrok URLs to the ALLOWED_HOSTS list:

   ```
   ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.ngrok-free.dev',
   ]
   ```
5. Notes:
   - Ensure your dev server is reachable on the same port you expose with ngrok.
   - If DEBUG = False, add the ngrok host to ALLOWED_HOSTS.
   - Use Mollie test API keys while testing; switch to live keys for production.

You can now test payment flows and webhook handling locally using the public ngrok URL. Fill in any project-specific webhook paths and environment variables as needed.

---

## Tips & gotchas

- Always assign `.choices` properly when using Django `TextChoices` enums: use `MyEnum.choices`, not the class itself.
- When constructing form choices dynamically in views, assign `form.fields['fieldname'].choices = ...` before rendering or validating.
- When attaching files to EmailMultiAlternatives, `pdf_buffer.seek(0)` is required before `pdf_buffer.read()`.
- Use consistent field names across form, view and template (e.g., `dimension` vs `dimensions`) — mismatches lead to invalid forms.
- Serve MEDIA files in dev with:
  ```
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

---

If you want, I can:
- Add the `.vscode/settings.json` file for test discovery.
- Add example env/sample settings for email.
- Generate a more detailed contributor/deployment section.