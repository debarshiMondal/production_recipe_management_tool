import os
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, url_for
from datetime import datetime
from fpdf import FPDF

sales_management_bp = Blueprint('sales_management', __name__)

@sales_management_bp.route('/sales-management', methods=['GET'])
def sales_management():
    return render_template('sales_management/sales_management.html')

@sales_management_bp.route('/sales-management/pos', methods=['GET'])
def pos():
    return render_template('sales_management/pos.html')

@sales_management_bp.route('/sales-management/pos/b2b', methods=['GET'])
def pos_b2b():
    return render_template('sales_management/pos_b2b.html')

@sales_management_bp.route('/sales-management/pos/catering', methods=['GET'])
def pos_catering():
    return render_template('sales_management/pos_catering.html')

@sales_management_bp.route('/sales-management/procurement-costs', methods=['GET'])
def procurement_costs():
    return render_template('sales_management/procurement_costs.html')

@sales_management_bp.route('/sales-management/sales-reports', methods=['GET'])
def sales_reports():
    return render_template('sales_management/sales_reports.html')

@sales_management_bp.route('/sales-management/ledger', methods=['GET'])
def ledger():
    return render_template('sales_management/ledger.html')

@sales_management_bp.route('/sales-management/pos/offline')
def pos_offline():
    dish_folder = 'data/Dish'
    dishes = []
    if os.path.exists(dish_folder):
        for filename in os.listdir(dish_folder):
            if filename.endswith('.xlsx'):
                dish_name = filename.split('-OffSP-')[0]
                offline_price = filename.split('-OffSP-')[1].split('OnSP-')[0]
                online_price = filename.split('OnSP-')[1].replace('.xlsx', '')
                dishes.append({
                    'name': dish_name,
                    'offlinePrice': offline_price,
                    'onlinePrice': online_price
                })
    return render_template('sales_management/pos_offline.html', dishes=dishes)

@sales_management_bp.route('/upload-dish', methods=['POST'])
def upload_dish():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    if file:
        filename = file.filename
        file.save(os.path.join('data/Dish', filename))
        return jsonify({'success': True})

@sales_management_bp.route('/get-dishes', methods=['GET'])
def get_dishes():
    dish_folder = 'data/Dish'
    dishes = []
    if os.path.exists(dish_folder):
        for filename in os.listdir(dish_folder):
            if filename.endswith('.xlsx'):
                dish_name = filename.split('-OffSP-')[0]
                offline_price = filename.split('-OffSP-')[1].split('OnSP-')[0]
                online_price = filename.split('OnSP-')[1].replace('.xlsx', '')
                dishes.append({
                    'name': dish_name,
                    'offlinePrice': offline_price,
                    'onlinePrice': online_price
                })
    return jsonify({'dishes': dishes})

@sales_management_bp.route('/get-add-ons', methods=['GET'])
def get_add_ons():
    raw_material_list = 'data/Raw_Material_List.xlsx'
    add_ons = []
    if os.path.exists(raw_material_list):
        df = pd.read_excel(raw_material_list)
        add_ons = df[['Product', 'Unit Cost']].to_dict('records')
    return jsonify({'add_ons': add_ons})

@sales_management_bp.route('/generate-bill', methods=['POST'])
def generate_bill():
    try:
        data = request.get_json()
        customer_name = data.get('customerName')
        customer_phone = data.get('customerPhone')
        date = datetime.now().strftime("%Y-%m-%d")
        bill_number = get_next_number('data/Bill Number.txt')
        order_number = get_next_number('data/Order ID.txt')
        dishes = data.get('dishes', [])
        add_ons = data.get('add_ons', [])
        discount = data.get('discount', 0)
        discount_type = data.get('discountType')
        tax = data.get('tax', 0)
        final_subtotal = data.get('finalSubtotal', 0)

        # Get company information from request
        company_name = data.get('companyName')
        company_phone = data.get('companyPhone')
        company_email = data.get('companyEmail')
        company_address = data.get('companyAddress')

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=8)
        
        # Add company information
        pdf.set_font("Arial", size=10, style='B')
        pdf.cell(0, 5, txt=f"{company_name}", ln=True, align="C")
        pdf.set_font("Arial", size=8)
        pdf.cell(0, 5, txt=f"Phone: {company_phone}", ln=True, align="C")
        pdf.cell(0, 5, txt=f"Email: {company_email}", ln=True, align="C")
        pdf.cell(0, 5, txt=f"Address: {company_address}", ln=True, align="C")
        pdf.ln(10)

        # Add bill title
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(0, 10, txt="Invoice", ln=True, align="C")
        pdf.ln(5)

        # Add customer and order information
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, txt=f"Bill To:", ln=True, align="L")
        pdf.cell(0, 5, txt=f"Customer Name: {customer_name}", ln=True)
        pdf.cell(0, 5, txt=f"Customer Phone: {customer_phone}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 5, txt=f"Date: {date}", ln=True, align="R")
        pdf.cell(0, 5, txt=f"Bill Number: {bill_number}", ln=True, align="R")
        pdf.cell(0, 5, txt=f"Invoice Number: {order_number}", ln=True, align="R")
        pdf.ln(5)

        # Add table headers
        pdf.set_font("Arial", size=10, style='B')
        pdf.cell(60, 10, txt="Item", border=1, align="C")
        pdf.cell(30, 10, txt="Quantity", border=1, align="C")
        pdf.cell(30, 10, txt="Unit Price", border=1, align="C")
        pdf.cell(30, 10, txt="Total", border=1, align="C")
        pdf.ln(10)

        # Add table rows
        pdf.set_font("Arial", size=10)
        total_price = 0
        for dish in dishes:
            dish_total = dish['price']
            pdf.cell(60, 10, txt=dish['name'], border=1)
            pdf.cell(30, 10, txt="1", border=1, align="C")
            pdf.cell(30, 10, txt=f"{dish['price']:.2f}", border=1, align="R")
            pdf.cell(30, 10, txt=f"{dish_total:.2f}", border=1, align="R")
            pdf.ln(10)
            total_price += dish_total

        if add_ons:
            for add_on in add_ons:
                add_on_total_price = add_on['qty'] * add_on['price']
                pdf.cell(60, 10, txt=add_on['name'], border=1)
                pdf.cell(30, 10, txt=f"{add_on['qty']} {add_on['unit']}", border=1, align="C")
                pdf.cell(30, 10, txt=f"{add_on['price']:.2f}", border=1, align="R")
                pdf.cell(30, 10, txt=f"{add_on_total_price:.2f}", border=1, align="R")
                pdf.ln(10)
                total_price += add_on_total_price

        # Calculate totals
        if discount_type == 'percent':
            discount_amount = (total_price * discount / 100)
        else:
            discount_amount = discount

        total_price -= discount_amount
        total_price += (tax / 100) * total_price

        # Add totals to the bill
        pdf.set_font("Arial", size=10, style='B')
        pdf.cell(120, 10, txt="Subtotal", border=1)
        pdf.cell(30, 10, txt=f"{total_price + discount_amount:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Discount", border=1)
        pdf.cell(30, 10, txt=f"{discount_amount:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Tax (%)", border=1)
        pdf.cell(30, 10, txt=f"{tax:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Final Subtotal", border=1)
        pdf.cell(30, 10, txt=f"{final_subtotal:.2f}", border=1, align="R")

        pdf_output_path = os.path.join('static/bills', f"Bill_{date}_{customer_name}.pdf")
        if not os.path.exists('static/bills'):
            os.makedirs('static/bills')
        pdf.output(pdf_output_path)

        # Generate the Excel file for sales data
        sales_data = []
        for dish in dishes:
            sales_data.append({
                'Date': date,
                'Dish Name': dish['name'],
                'Offline Price': dish['price'],
                'Add On': '',
                'Add On Cost': '',
                'Add On Price': ''
            })

        if add_ons:
            for add_on in add_ons:
                sales_data.append({
                    'Date': date,
                    'Dish Name': '',
                    'Offline Price': '',
                    'Add On': add_on['name'],
                    'Add On Cost': add_on['qty'],
                    'Add On Price': add_on['price']
                })

        sales_df = pd.DataFrame(sales_data)
        sales_folder = 'data/Sales'
        if not os.path.exists(sales_folder):
            os.makedirs(sales_folder)
        excel_filename = f"{date}_{bill_number}_T{total_price}_D{discount_amount}_T{tax}_FS{final_subtotal}.xlsx"
        sales_df.to_excel(os.path.join(sales_folder, excel_filename), index=False)

        return jsonify({'success': True, 'billLink': url_for('static', filename=f'bills/Bill_{date}_{customer_name}.pdf')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_management_bp.route('/generate-kot', methods=['POST'])
def generate_kot():
    try:
        data = request.get_json()
        date = datetime.now().strftime("%Y-%m-%d")
        bill_number = get_next_number('data/Bill Number.txt')
        order_number = get_next_number('data/Order ID.txt')
        dishes = data.get('dishes', [])
        add_ons = data.get('add_ons', [])

        # Create PDF
        pdf = FPDF(orientation='P', unit='mm', format='A5')
        pdf.add_page()
        pdf.set_font("Arial", size=8)

        # Print KOT in triplicate
        for i in range(3):
            if i > 0:
                pdf.add_page()

            # Add order and bill information
            pdf.cell(0, 5, txt=f"Order ID: {order_number}", ln=True, align="L")
            pdf.cell(0, 5, txt=f"Date: {date}", ln=True, align="L")
            pdf.cell(0, 5, txt=f"Bill Number: {bill_number}", ln=True, align="L")

            # Add dishes
            for dish in dishes:
                pdf.cell(0, 5, txt=f"Dish: {dish['name']}", ln=True, align="L")

            # Add add-ons
            if add_ons:
                pdf.cell(0, 5, txt="Add Ons:", ln=True, align="L")
                for add_on in add_ons:
                    pdf.cell(0, 5, txt=f"{add_on['name']}: {add_on['qty']} {add_on['unit']}", ln=True, align="L")

            pdf.ln(5)

        pdf_output_path = os.path.join('static/kots', f"KOT_{date}_{bill_number}.pdf")
        if not os.path.exists('static/kots'):
            os.makedirs('static/kots')
        pdf.output(pdf_output_path, 'F')

        return jsonify({'success': True, 'kotLink': url_for('static', filename=f'kots/KOT_{date}_{bill_number}.pdf')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_next_number(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('1')
    with open(file_path, 'r') as f:
        content = f.read().strip()
        if not content:
            number = 1
        else:
            number = int(content) + 1
    with open(file_path, 'w') as f:
        f.write(str(number))
    return number
