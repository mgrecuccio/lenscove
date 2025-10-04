# LensCove

LensCove is a Django-based web application that allows customers to browse, order, and customize fine art prints of images. Users can select image dimensions, frame color, and frame type to personalize their orders.

## Python & Django Versions

- **Python:** 3.11
- **Django:** 5.2.6
- **Bootstrap:** 5.3.8


*(Versions are based on the requirements.txt file. Please verify your environment matches these requirements.)*

## Pages

- **Home:** Browse featured images and collections.
- **Gallery:** View all available images for ordering.
- **Image Detail:** See details and customization options for each image.
- **Order Page:** Customize and place orders for fine art prints.
- **Cart:** Review selected items before checkout.
- **Checkout:** Enter shipping and payment information.
- **Order Confirmation:** View order summary and confirmation.
- **Admin:** Manage images, orders, and customers (for staff).

## Features

- Browse and search a curated gallery of images.
- Order images as fine art prints.
- Customize print orders:
  - Select image dimensions.
  - Choose frame color.
  - Choose frame type.
- Add multiple items to cart and checkout.
- Receive order confirmation and summary.
- Admin interface for managing content and orders.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lenscove.git
cd lenscove
```

### 2. Create and Activate a Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

### 6. Access the Application

Open your browser and go to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

For admin access, create a superuser:

```bash
python manage.py createsuperuser
```

---

**Enjoy customizing and ordering fine art prints with LensCove! :)**