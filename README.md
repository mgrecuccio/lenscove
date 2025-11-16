# 🖼️ LensCove — Fine-Art Print E-Commerce

**LensCove** is a full e-commerce web application for browsing, customizing, and ordering fine-art photographic prints.  
It includes a complete checkout workflow, online payments (Mollie), shipping label creation & tracking (Shippo), PDF invoicing, email notifications, and a clean Bootstrap-based UI.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Local Development (non-Docker)](#-local-development-non-docker)
- [Docker Development Setup](#-docker-development-setup)
  - [Environment Variables](#environment-variables)
  - [Start Containers](#start-containers)
  - [Apply Migrations](#apply-migrations)
  - [Accessing Postgres via TablePlus](#accessing-postgres)
  - [Resetting the DB](#resetting-the-db)
- [Running Tests](#-running-tests)
- [Mollie Payments Setup](#-payments-mollie)
- [Shippo Shipping Setup](#-shipping-shippo)
- [Deployment Notes](#-deployment-notes)
- [Roadmap](#-roadmap)
- [Troubleshooting](#-troubleshooting)
- [Badges](#-badges)

---

# 🌟 Features

✔ Browse curated image collections  
✔ Product detail pages with dimension & frame selection  
✔ Session-based shopping cart  
✔ Checkout flow with Order + OrderItem models  
✔ Online payments via **Mollie**  
✔ Shipping label creation via **Shippo**  
✔ Real shipment tracking + webhook updates  
✔ PDF invoice generation (ReportLab)  
✔ Email notifications (customer + admin)  
✔ Full admin interface (Django admin)  
✔ Dockerized environment with PostgreSQL  
✔ SQLite-based in-memory tests for speed  

---

# 🧱 Tech Stack

- **Python** 3.13  
- **Django** 5.2.6  
- **PostgreSQL 16**  
- **Docker & Docker Compose**  
- **Bootstrap 5 (Cerulean)**  
- **ReportLab** for PDF invoices  
- **Mollie** for payments  
- **Shippo** for shipping  

---

# 📂 Project Structure

```
lenscove/
│
├── config/
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       └── test.py
│
├── store/
├── cart/
├── orders/
├── payments/
├── shipping/
├── contacts/
│
├── templates/
├── static/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

# 🧰 Local Development (non-Docker)

```bash
git clone https://github.com/mgrecuccio/lenscove.git
cd lenscove
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

---

# 🐳 Docker Development Setup

This is the recommended way to develop LensCove.

## Environment Variables

Create `.env`:

```
SECRET_KEY=your-secret-key
POSTGRES_DB=lenscove_dev
POSTGRES_USER=lenscove
POSTGRES_PASSWORD=lenscove
POSTGRES_HOST=db
POSTGRES_PORT=5432

MOLLIE_API_KEY=test_xxx
SHIPPO_API_KEY=shippo_test_xxx
```

---

## Start Containers

```bash
docker-compose up --build
```

App → http://localhost:8000  
Admin → http://localhost:8000/admin  

---

## Apply Migrations

```bash
docker-compose exec web python manage.py migrate
```

Create admin user:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Accessing Postgres

### Using TablePlus

```
Host: localhost
Port: 5432
User: lenscove
Password: lenscove
Database: lenscove_dev
```

### Using psql

```bash
docker-compose exec db psql -U lenscove -d lenscove_dev
```

---

## Resetting the DB

```bash
docker-compose down -v
docker-compose up --build
docker-compose exec web python manage.py migrate
```

---

# 🧪 Running Tests

```bash
python manage.py test
```

Uses **SQLite in-memory** for speed.

---

# 💳 Payments (Mollie)

- Create account on https://mollie.com
- Add API key to `.env`
- Use ngrok for local callbacks:

```
ngrok http 8000
```

Then configure:

```
MOLLIE_REDIRECT_URL=https://<id>.ngrok.app/payments/return/
MOLLIE_WEBHOOK_URL=https://<id>.ngrok.app/payments/webhook/
```

---

# 📦 Shipping (Shippo)

- Create account at https://goshippo.com
- Add API key to `.env`
- Create local test shipments**
   
```bash
python manage.py create_test_shippo_shipment SHIPPO_DELIVERED
```
- Configure webhook:

```
https://<ngrok>.ngrok.app/shipping/webhook/
```

Test webhook:

```bash
curl -X POST http://127.0.0.1:8000/shipping/webhook/   -H "Content-Type: application/json"   -d '{"event":"track_updated","data":{"tracking_status":{"status":"DELIVERED"},"tracking_number":"SHIPPO_DELIVERED"}}'
```

---

## 📨 Contact & Messaging 

LensCove includes a complete **Contact App** that lets customers reach
out for product inquiries, order questions, shipment info, or
collaboration requests.

#### Main Capabilities

-   Public Bootstrap 5 contact form\
-   All fields required\
-   Saves message to DB\
-   Sends admin notification\
-   Sends customer auto-reply\
-   HTML + text email templates

#### Email Templates

    templates/emails/contact_notification.html
    templates/emails/contact_notification.txt
    templates/emails/contact_autoreply.html
    templates/emails/contact_autoreply.txt

#### Settings

    DEFAULT_FROM_EMAIL=no-reply@lenscove.com
    CONTACT_RECEIVER_EMAIL=admin@lenscove.com

----
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

# ☁️ Deployment Notes

```bash
python manage.py collectstatic
python manage.py migrate --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

# 🛣️ Roadmap

- User accounts  
- Discount codes  
- Multi-currency  
- Print-on-demand integration  
- Admin shipping dashboard  
- CDN for media  

---

# 🩺 Troubleshooting

| Issue | Fix |
|------|-----|
| Cannot connect to Postgres | Stop macOS Postgres: `brew services stop postgresql` |
| Tables missing in TablePlus | You connected to local Postgres instead of Docker |
| SECRET_KEY empty | `.env` not loading — fix BASE_DIR |
| dumpdata errors | Use `--settings=config.settings.test` |

---

# 🧩 Badges

![Python](https://img.shields.io/badge/python-3.13-blue)
![Django](https://img.shields.io/badge/django-5.2.6-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)