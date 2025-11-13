# 🖼️ LensCove

**LensCove** is a Django web application for browsing, customizing, and ordering fine-art prints.  
Customers can choose image dimensions, frame type and color, add items to a cart, complete checkout with Mollie, and receive a confirmation email with a PDF invoice and shipment tracking.

---

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Key Pages](#key-pages)
- [Main Features](#main-features)
- [Project Structure](#project-structure)
- [Setup (macOS)](#setup-macos)
- [Running Tests](#running-tests)
- [Payments (Mollie)](#payments-gateway-setup)
- [Shipping (Shippo)](#shipment-provider-setup)
- [Deployment Notes](#deployment-notes)
- [Roadmap / Future Ideas](#roadmap--future-ideas)
- [Tips & Gotchas](#tips--gotchas)

---

## 🚀 Quick Start

```bash
git clone https://github.com/mgrecuccio/lenscove.git
cd lenscove
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then visit 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ⚙️ Tech Stack

- **Python** 3.13  
- **Django** 5.2.6  
- Other dependencies listed in `requirements.txt`

---

## 🖼️ Key Pages

- **Home** — featured and best sellers  
- **Gallery** — browse collections and products  
- **Product Detail** — choose image, dimension, and frame options  
- **Cart** — review, update, and remove items  
- **Checkout (Order Create)** — enter contact and shipping info  
- **Payment (Mollie)** — secure online payment  
- **Order Confirmation** — summary and downloadable invoice  
- **Admin** — manage products, categories, and orders  

---

## 💡 Main Features

- Browse curated image galleries  
- Order fine-art prints with:
  - Dimensions (10×15, 13×18, 20×30, etc.)
  - Frame type and color  
  - Quantity controls  
- Full cart management (add / update / remove)  
- Checkout flow creating `Order` and `OrderItem` records  
- Secure payment with **Mollie**  
- Email notifications:
  - HTML + plain text email to customer  
  - PDF invoice attachment (via ReportLab)  
- Shipment label creation and tracking via **Shippo**  
- Unit tests for views, utilities, and email/invoice logic  
- Responsive **Bootstrap 5** (Cerulean theme)

---

## 🗂️ Project Structure

| App | Responsibility |
|-----|----------------|
| **store/** | Products, categories, gallery views |
| **cart/** | Session-based cart logic and views |
| **orders/** | Order models, checkout, invoices, and email |
| **payments/** | Mollie integration |
| **shipping/** | Shippo integration and tracking webhooks |
| **templates/** | HTML & email templates |
| **static/** | CSS, JS, and images |
| **config/** | Global settings and URL routing |

---

## 🧰 Setup (macOS)

1. **Clone and create a virtual environment**
   ```bash
   git clone https://github.com/mgrecuccio/lenscove.git
   cd lenscove
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment configuration**
   Copy `.env.example` to `.env` and update as needed:
   ```bash
   SECRET_KEY=your_secret
   MOLLIE_API_KEY=test_xxx
   SHIPPO_API_KEY=shippo_test_xxx
   EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
   EMAIL_FILE_PATH=tmp/emails
   ```

3. **Apply migrations and create superuser**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server**
   ```bash
   python manage.py runserver
   ```
   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧪 Running Tests

```bash
python manage.py test
```

**VS Code integration (optional):**  
`.vscode/settings.json`
```json
{
  "python.testing.unittestEnabled": true,
  "python.testing.unittestArgs": ["-v", "-s", ".", "-p", "test_*.py"],
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

---

## 💳 Payments Gateway Setup (Mollie)

1. **Create a Mollie account:** [https://www.mollie.com](https://www.mollie.com)  
2. Switch to **Test mode** and obtain your test API key (`test_...`).  
3. Add in settings or `.env`:
   ```bash
   MOLLIE_API_KEY=test_xxx
   ```
4. Expose your local server with **ngrok**:
   ```bash
   ngrok http 8000
   ```
   Then configure redirect/webhook URLs in Mollie using the ngrok domain:
   ```
   MOLLIE_REDIRECT_URL=https://<ngrok-id>.ngrok.io/payments/return/
   MOLLIE_WEBHOOK_URL=https://<ngrok-id>.ngrok.io/payments/webhook/
   ```
5. Add ngrok hosts to allowed hosts:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.dev']
   ```

Use Mollie’s sandbox for test transactions and webhook simulations.

---

## 📦 Shipment Provider Setup (Shippo)

1. **Create a Shippo account** — [https://goshippo.com](https://goshippo.com)  
   Use test mode and generate an API key:
   ```bash
   SHIPPO_API_KEY=shippo_test_xxx
   SHIPPO_WEBHOOK_URL=https://your-ngrok-id.ngrok.io/shipping/webhook/
   ```

2. **Webhook configuration**
   - In the Shippo Dashboard, add your ngrok URL as a webhook target.  
   - Example endpoint: `https://<ngrok-id>.ngrok.io/shipping/webhook/`.

3. **Simulate tracking events in sandbox**
   - `SHIPPO_TRANSIT` → in transit  
   - `SHIPPO_DELIVERED` → delivered  
   - `SHIPPO_RETURNED` → returned  
   - `SHIPPO_FAILURE` → failed delivery  

4. **Test locally**
   ```bash
   curl -X POST http://127.0.0.1:8000/shipping/webhook/    -H "Content-Type: application/json"    -d '{
         "event": "track_updated",
         "data": {
           "tracking_number": "SHIPPO_DELIVERED",
           "tracking_status": {"status": "DELIVERED"}
         }
       }'
   ```

5. **Create local test shipments**
   ```bash
   python manage.py create_test_shippo_shipment SHIPPO_DELIVERED
   ```

Use ngrok’s dashboard (`http://127.0.0.1:4040`) to inspect incoming requests.

---

## ☁️ Deployment Notes

LensCove runs on any WSGI-compatible host.

**Recommended stack:**
- PostgreSQL  
- Gunicorn + Nginx  
- Environment config via `.env` or secrets manager  

**Deploy steps:**
```bash
python manage.py collectstatic
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Set `DEBUG=False` and configure `ALLOWED_HOSTS` and secure API keys.

---

## 🛠️ Roadmap / Future Ideas

- User accounts and order history  
- Coupon codes and promotions  
- Print-on-demand provider integration (e.g., Printful)  
- Admin shipping dashboard / analytics  
- Full Docker + PostgreSQL deployment  

---

## ⚠️ Tips & Gotchas

- Use `.choices` from `TextChoices`, not the class itself  
- Assign form `.choices` dynamically *before* validation  
- Reset PDF buffer with `pdf_buffer.seek(0)` before reading  
- Ensure consistent field names between form, view, and template  
- Serve MEDIA in dev:
  ```python
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

---

## 🧩 Badges

![Python](https://img.shields.io/badge/python-3.13-blue)
![Django](https://img.shields.io/badge/django-5.2.6-green)

---

✅ **In summary:**  
LensCove provides a full end-to-end fine-art print e-commerce workflow with payments, invoices, and shipment tracking — ready for production deployment.
