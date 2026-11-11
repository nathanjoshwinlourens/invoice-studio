import os
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

@app.route('/')
def index():
    # Renders our interactive HTML builder page
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # 1. Capture incoming form data from the PM's user interface
    biz_name = request.form.get('biz_name', 'Your Business Name')
    client_name = request.form.get('client_name', 'Client Name')
    invoice_num = request.form.get('invoice_num', 'INV-001')
    bank_details = request.form.get('bank_details', '')
    
    # Process dynamic items (names, quantities, prices)
    item_names = request.form.getlist('item_name[]')
    item_qtys = request.form.getlist('item_qty[]')
    item_prices = request.form.getlist('item_price[]')

    pdf_filename = f"invoice_{invoice_num}.pdf"
    
    # 2. Setup PDF document constraints
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # 3. Define typography typography and color palettes
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor("#1e3a8a"))
    normal_style = styles['Normal']
    bold_style = ParagraphStyle('BoldText', parent=styles['Normal'], fontName='Helvetica-Bold')
    footer_style = ParagraphStyle('FooterText', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)

    # Add header components
    story.append(Paragraph(f"<b>{biz_name}</b>", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"<b>Invoice Number:</b> {invoice_num}", normal_style))
    story.append(Paragraph(f"<b>Billed To:</b> {client_name}", normal_style))
    story.append(Spacer(1, 20))

    # 4. Construct the line item calculation table
    table_data = [[Paragraph("<b>Description</b>", normal_style), Paragraph("<b>Qty</b>", normal_style), Paragraph("<b>Unit Price (ZAR)</b>", normal_style), Paragraph("<b>Total (ZAR)</b>", normal_style)]]
    
    grand_total = 0.0
    for name, qty, price in zip(item_names, item_qtys, item_prices):
        if not name: continue
        try:
            q = int(qty) if qty else 1
            p = float(price) if price else 0.0
        except ValueError:
            qStr, p = 1, 0.0
            
        row_total = q * p
        grand_total += row_total
        table_data.append([Paragraph(name, normal_style), str(q), f"R {p:,.2f}", f"R {row_total:,.2f}"])

    # Append Grand Total Row
    table_data.append(["", "", Paragraph("<b>Grand Total:</b>", bold_style), Paragraph(f"<b>R {grand_total:,.2f}</b>", bold_style)])

    # Style table with professional corporate layout
    invoice_table = Table(table_data, colWidths=[250, 50, 100, 120])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f3f4f6")),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#e5e7eb")),
        ('LINEBELOW', (0,-2), (-1,-2), 1, colors.HexColor("#1e3a8a")), # Line above total
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 30))

    # 5. Append critical payment details if provided
    if bank_details:
        story.append(Paragraph("<b>Payment Information:</b>", bold_style))
        story.append(Paragraph(bank_details.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 40))

    # 6. Built-in Monetisation Engine (Free user credit watermark)
    story.append(Paragraph("Generated via Professional Invoice Studio. Upgrade to premium to remove this watermark.", footer_style))

    # Build the document binary
    doc.build(story)

    # Send the finished PDF back directly to the client browser for download
    return send_file(pdf_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
