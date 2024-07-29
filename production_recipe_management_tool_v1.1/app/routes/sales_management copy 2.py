import os
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, send_from_directory
from datetime import datetime
from fpdf import FPDF

sales_management_bp = Blueprint('sales_management', __name__)

@sales_management_bp.route('/sales-management', methods=['GET'])
def sales_management():
    return render_template('sales_management/sales_management.html')

@sales_management_bp.route('/sales-management/pos', methods=['GET'])
def pos():
    return render_template('sales_management/pos.html')

@sales_management_bp.route('/sales-management/pos/offline', methods=['GET'])
def offline():
    outlets_dir = 'data/Outlets'
    outlets = []
    if os.path.exists(outlets_dir):
        outlets = os.listdir(outlets_dir)
    return render_template('sales_management/pos_offline.html', outlets=outlets)

@sales_management_bp.route('/sales-management/pos/online', methods=['GET'])
def online():
    return render_template('sales_management/pos_online.html')

@sales_management_bp.route('/sales-management/pos/offline/<outlet>', methods=['GET'])
def pos_offline(outlet):
    outlet_dir = os.path.join('data/Outlets', outlet)
    dish_folder = os.path.join(outlet_dir, 'Dish')
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

    # Read outlet information
    outlet_info_path = os.path.join(outlet_dir, 'OutletInfo.txt')
    outlet_info = {}
    if os.path.exists(outlet_info_path):
        with open(outlet_info_path, 'r') as f:
            for line in f:
                key, value = line.split(': ')
                outlet_info[key.strip()] = value.strip()

    return render_template('sales_management/pos_offline_outlet.html', dishes=dishes, outlet=outlet, outlet_info=outlet_info)

@sales_management_bp.route('/sales-management/pos/create-outlet', methods=['GET', 'POST'])
def create_outlet():
    if request.method == 'POST':
        outlet_name = request.form.get('outletName')
        outlet_phone = request.form.get('outletPhone')
        outlet_email = request.form.get('outletEmail')
        outlet_address = request.form.get('outletAddress')
        
        # Create outlet directory structure
        outlet_dir = os.path.join('data/Outlets', outlet_name)
        os.makedirs(outlet_dir, exist_ok=True)
        os.makedirs(os.path.join(outlet_dir, 'Dish'), exist_ok=True)
        os.makedirs(os.path.join(outlet_dir, 'Bills'), exist_ok=True)
        os.makedirs(os.path.join(outlet_dir, 'Sales'), exist_ok=True)
        os.makedirs(os.path.join(outlet_dir, 'KOTs'), exist_ok=True)
        
        # Create Bill Number and Order ID files
        with open(os.path.join(outlet_dir, 'Bill Number.txt'), 'w') as f:
            f.write('1')
        with open(os.path.join(outlet_dir, 'Order ID.txt'), 'w') as f:
            f.write('1')
        
        # Save outlet information
        outlet_info = f"Name: {outlet_name}\nPhone: {outlet_phone}\nEmail: {outlet_email}\nAddress: {outlet_address}"
        with open(os.path.join(outlet_dir, 'OutletInfo.txt'), 'w') as f:
            f.write(outlet_info)
        
        return redirect(url_for('sales_management.offline'))

    return render_template('sales_management/create_outlet.html')

@sales_management_bp.route('/delete-outlet/<outlet>', methods=['POST'])
def delete_outlet(outlet):
    outlet_dir = os.path.join('data/Outlets', outlet)
    if os.path.exists(outlet_dir):
        import shutil
        shutil.rmtree(outlet_dir)
    return redirect(url_for('sales_management.offline'))

@sales_management_bp.route('/upload-dish/<outlet>', methods=['POST'])
def upload_dish(outlet):
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    outlet_dir = os.path.join('data/Outlets', outlet)
    dish_folder = os.path.join(outlet_dir, 'Dish')
    
    if file:
        filename = file.filename
        file_path = os.path.join(dish_folder, filename)
        if os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'File already exists'})
        file.save(file_path)
        return jsonify({'success': True})

@sales_management_bp.route('/get-dishes/<outlet>', methods=['GET'])
def get_dishes(outlet):
    outlet_dir = os.path.join('data/Outlets', outlet)
    dish_folder = os.path.join(outlet_dir, 'Dish')
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
        outlet = data.get('outlet')
        customer_name = data.get('customerName')
        customer_phone = data.get('customerPhone')
        date = datetime.now().strftime("%Y-%m-%d")
        outlet_dir = os.path.join('data/Outlets', outlet)
        bill_number = get_next_number(os.path.join(outlet_dir, 'Bill Number.txt'))
        order_number = get_next_number(os.path.join(outlet_dir, 'Order ID.txt'))
        dishes = data.get('dishes', [])
        add_ons = data.get('add_ons', [])
        discount = data.get('discount', 0)
        discount_type = data.get('discountType')
        tax = data.get('tax', 0)
        final_subtotal = data.get('finalSubtotal', 0)

        # Get company information from outlet info file
        with open(os.path.join(outlet_dir, 'OutletInfo.txt'), 'r') as f:
            outlet_info = f.read().strip().split('\n')
            company_name = outlet_info[0].split(': ')[1]
            company_phone = outlet_info[1].split(': ')[1]
            company_email = outlet_info[2].split(': ')[1]
            company_address = outlet_info[3].split(': ')[1]

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

        pdf_output_path = os.path.join(outlet_dir, 'Bills', f"Bill_{date}_{customer_name}.pdf")
        if not os.path.exists(os.path.join(outlet_dir, 'Bills')):
            os.makedirs(os.path.join(outlet_dir, 'Bills'))
        pdf.output(pdf_output_path)

        return jsonify({'success': True, 'billLink': url_for('sales_management.download_bill', outlet=outlet, date=date, customer_name=customer_name)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_management_bp.route('/generate-kot', methods=['POST'])
def generate_kot():
    try:
        data = request.get_json()
        outlet = data.get('outlet')
        date = datetime.now().strftime("%Y-%m-%d")
        outlet_dir = os.path.join('data/Outlets', outlet)
        bill_number = get_next_number(os.path.join(outlet_dir, 'Bill Number.txt'))
        order_number = get_next_number(os.path.join(outlet_dir, 'Order ID.txt'))
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

            # Add outlet name
            pdf.cell(0, 5, txt=f"Outlet: {outlet}", ln=True, align="L")
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
                    pdf.cell(60, 5, txt=f"{add_on['name']}", ln=True, align="L")
                    pdf.cell(30, 5, txt=f"{add_on['qty']}", ln=True, align="L")
                    pdf.cell(30, 5, txt=f"{add_on['unit']}", ln=True, align="L")

            pdf.ln(5)

        pdf_output_path = os.path.join(outlet_dir, 'KOTs', f"KOT_{date}_{bill_number}.pdf")
        if not os.path.exists(os.path.join(outlet_dir, 'KOTs')):
            os.makedirs(os.path.join(outlet_dir, 'KOTs'))
        pdf.output(pdf_output_path, 'F')

        return jsonify({'success': True, 'kotLink': url_for('sales_management.download_kot', outlet=outlet, date=date, bill_number=bill_number)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@sales_management_bp.route('/download-bill/<outlet>/<date>/<customer_name>', methods=['GET'])
def download_bill(outlet, date, customer_name):
    directory = os.path.join('data/Outlets', outlet, 'Bills')
    filename = f"Bill_{date}_{customer_name}.pdf"
    return send_from_directory(directory, filename)

@sales_management_bp.route('/download-kot/<outlet>/<date>/<bill_number>', methods=['GET'])
def download_kot(outlet, date, bill_number):
    directory = os.path.join('data/Outlets', outlet, 'KOTs')
    filename = f"KOT_{date}_{bill_number}.pdf"
    return send_from_directory(directory, filename)

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
