from fpdf import FPDF
from io import BytesIO

def generate_estimation_pdf(estimation_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Title
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Estimation of Production", ln=True, align='C')

    # Table headers
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(120, 10, txt="Item", border=1)
    pdf.cell(30, 10, txt="Quantity", border=1)
    pdf.cell(30, 10, txt="Subtotal", border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", size=7)
    total_cost = 0
    for index, row in estimation_df.iterrows():
        item_name = row['Item'].rsplit('_', 2)[2].rsplit('.', 1)[0]  # Extracting the item name from filename

        # Split item name if it's too long
        if len(item_name) > 120:
            item_name = item_name[:40] + '\n' + item_name[40:]

        pdf.multi_cell(120, 10, txt=str(item_name), border=1)
        pdf.set_xy(pdf.get_x() + 120, pdf.get_y() - 10)  # Adjust x position after multi_cell
        pdf.cell(30, 10, txt=str(row['Quantity']), border=1)
        pdf.cell(30, 10, txt=str(row['Subtotal']), border=1)
        total_cost += row['Subtotal']
        pdf.ln()

    # Total cost
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(150, 10, txt="Total Cost", border=1)
    pdf.cell(30, 10, txt=f"{total_cost:.2f}", border=1)
    pdf.ln()

    # Output the PDF to a BytesIO object
    pdf_output = BytesIO()
    pdf_output_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_output_bytes)
    pdf_output.seek(0)

    return pdf_output
