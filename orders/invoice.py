import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from reportlab.lib.utils import ImageReader
from PIL import Image


def generate_invoice(order):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Company Logo ---
    try:
        logo_path = os.path.join(settings.BASE_DIR, settings.SHOP_LOGO)

        img = Image.open(logo_path)

        # 2️⃣ Convert transparency and color mode
        # If image has an alpha channel, blend it on a white background
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        max_width = 50
        w_percent = max_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.LANCZOS)

        # 4️⃣ Convert Pillow image to a ReportLab ImageReader
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)
        logo = ImageReader(img_io)

        # 5️⃣ Draw image in the PDF
        p.drawImage(logo, 50, height - 100, width=50, preserveAspectRatio=True, mask='auto')

    except Exception as e:
        print("Logo error:", e)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 100, settings.SHOP_NAME)


    # --- Company Details ---
    p.setFont("Helvetica", 10)
    p.drawString(350, height - 60, settings.SHOP_NAME)
    p.drawString(350, height - 75, settings.SHOP_ADDRESS)
    p.drawString(350, height - 90, f"Email: {settings.SHOP_EMAIL}")
    p.drawString(350, height - 105, f"Phone: {settings.SHOP_PHONE}")
    p.drawString(350, height - 120, f"VAT: {settings.SHOP_VAT}")

    # --- Invoice Header ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 165, f"Invoice #{order.id}")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 195, f"Customer: {order.first_name} {order.last_name}")
    p.drawString(50, height - 210, f"Email: {order.email}")
    p.drawString(50, height - 225, f"Address: {order.address}, {order.postal_code} {order.city}")

    # --- Table Header ---
    y = height - 275
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Product")
    p.drawString(360, y, "Quantity")
    p.drawString(410, y, "Unit Price")
    p.drawString(500, y, "Total")

    # --- Table Rows ---
    y -= 20
    p.setFont("Helvetica", 11)
    for item in order.items.all():
        p.drawString(50, y, item.product.title)
        p.drawString(360, y, str(item.quantity))
        p.drawString(410, y, f"{item.price} €")
        p.drawString(500, y, f"{item.get_cost()} €")
        y -= 20

    # --- Total ---
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(410, y, "Total:")
    p.drawString(500, y, f"{order.get_total_cost()} €")

    # --- Footer ---
    y -= 40
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, y, "Thank you for your purchase!")
    p.drawString(50, y - 15, "LensCove Shop")
    p.drawString(50, y - 50, "This is a computer-generated invoice and does not require a signature.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
