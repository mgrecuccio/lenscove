import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from . import logging


def generate_invoice(order):
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    page.setFont("Helvetica-Bold", 16)
    page.drawString(50, height - 50, f"Invoice #{order.id}")
    page.setFont("Helvetica", 12)
    page.drawString(50, height - 80, f"Customer: {order.first_name} {order.last_name}")
    page.drawString(50, height - 100, f"Email: {order.email}")
    page.drawString(50, height - 120, f"Address: {order.address}, {order.postal_code} {order.city}")

    # Table header
    y = height - 160
    page.setFont("Helvetica-Bold", 12)
    page.drawString(50, y, "Product")
    page.drawString(400, y, "Quantity")
    page.drawString(450, y, "Unit Price")
    page.drawString(520, y, "Total")

    # Table rows
    page.setFont("Helvetica", 12)
    y -= 20
    for item in order.items.all():
        page.drawString(50, y, item.product.title)
        page.drawString(400, y, str(item.quantity))
        page.drawString(450, y, f"{item.price} €")
        page.drawString(520, y, f"{item.get_cost()} €")
        y -= 20

    # Total
    y -= 20
    page.setFont("Helvetica-Bold", 12)
    page.drawString(400, y, "Total:")
    page.drawString(520, y, f"{order.get_total_cost()} €")

    # Footer
    y -= 40
    page.setFont("Helvetica-Oblique", 10)
    page.drawString(50, y, "Thank you for your purchase!")
    page.drawString(50, y - 15, "LensCove Team")

    page.showPage()
    page.save()
    buffer.seek(0)
    logging.info(f"Invoice PDF generated successfully for order id: {order.id}")
    return buffer
