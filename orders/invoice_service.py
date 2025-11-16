import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import mm
from django.conf import settings


class InvoiceService:

    @staticmethod
    def generate_invoice(order):
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=25 * mm,
            rightMargin=25 * mm,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="RightBold", alignment=TA_RIGHT, fontSize=10, leading=12, fontName="Helvetica-Bold"))
        styles.add(ParagraphStyle(name="NormalRight", alignment=TA_RIGHT, fontSize=10, leading=12))
        styles.add(ParagraphStyle(name="SectionTitle", fontSize=14, leading=16, spaceAfter=10, fontName="Helvetica-Bold"))

        elements = []

        # ======================
        #  LOGO + COMPANY INFO
        # ======================
        try:
            logo_path = os.path.join(settings.BASE_DIR, settings.SHOP_LOGO)

            from PIL import Image as PILImage
            pil_img = PILImage.open(logo_path)
            w, h = pil_img.size
            aspect = h / w
            
            display_width = 40 * mm
            display_height = display_width * aspect

            logo = Image(logo_path, width=display_width, height=display_height)

        except Exception:
            logo = Paragraph(f"<b>{settings.SHOP_NAME}</b>", styles["Title"])

        company_info = Paragraph(
            f"""
            <b>{settings.SHOP_NAME}</b><br/>
            {settings.SHOP_ADDRESS}<br/>
            Email: {settings.SHOP_EMAIL}<br/>
            Phone: {settings.SHOP_PHONE}<br/>
            VAT: {settings.SHOP_VAT}
            """,
            styles["Normal"]
        )

        header_table = Table(
            [[logo, "", company_info]],
            colWidths=[40*mm, 40*mm, None]
        )

        header_table.setStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
        ])

        elements.append(header_table)
        elements.append(Spacer(1, 15))

        # ======================
        #  INVOICE TITLE
        # ======================
        elements.append(Paragraph(f"Invoice #{order.id}", styles["SectionTitle"]))
        elements.append(Spacer(1, 8))

        # ======================
        #  CUSTOMER INFO
        # ======================
        customer_text = Paragraph(
            f"""
            <b>Customer:</b> {order.first_name} {order.last_name}<br/>
            <b>Email:</b> {order.email}<br/>
            <b>Address:</b> {order.address}, {order.postal_code} {order.city}
            """,
            styles["Normal"]
        )
        elements.append(customer_text)
        elements.append(Spacer(1, 20))

        # ======================
        #  ORDER ITEMS TABLE
        # ======================
        data = [["Product", "Qty", "Unit Price", "Total"]]

        for item in order.items.all():
            data.append([
                item.product.title,
                str(item.quantity),
                f"{item.price:.2f} €",
                f"{item.get_cost():.2f} €"
            ])

        data.append(["", "", Paragraph("<b>Total:</b>", styles["RightBold"]), f"{order.get_total_cost():.2f} €"])

        table = Table(
            data,
            colWidths=[80 * mm, 20 * mm, 35 * mm, 35 * mm]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 25))

        # ======================
        #  FOOTER
        # ======================
        footer = Paragraph(
            """
            Thank you for your purchase!<br/>
            <i>This invoice was generated automatically and does not require a signature.</i>
            """,
            styles["Normal"]
        )
        elements.append(footer)

        doc.build(elements)
        buffer.seek(0)
        return buffer