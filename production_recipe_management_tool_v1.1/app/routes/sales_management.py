import os
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, send_from_directory, send_file
from datetime import datetime, timedelta

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
    raw_material_list = 'data/Add_on_list.xlsx'
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
        tax_percentage = data.get('tax', 0)
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

        subtotal = total_price
        total_price -= discount_amount
        total_tax_amount = (tax_percentage / 100) * total_price
        total_price += total_tax_amount

        # Add totals to the bill
        pdf.set_font("Arial", size=10, style='B')
        pdf.cell(120, 10, txt="Subtotal", border=1)
        pdf.cell(30, 10, txt=f"{subtotal:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Discount", border=1)
        pdf.cell(30, 10, txt=f"{discount_amount:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Tax", border=1)
        pdf.cell(30, 10, txt=f"{total_tax_amount:.2f}", border=1, align="R")
        pdf.ln(10)
        pdf.cell(120, 10, txt="Final Subtotal", border=1)
        pdf.cell(30, 10, txt=f"{final_subtotal:.2f}", border=1, align="R")

        pdf_output_path = os.path.join(outlet_dir, 'Bills', f"Bill_{date}_{customer_name}.pdf")
        if not os.path.exists(os.path.join(outlet_dir, 'Bills')):
            os.makedirs(os.path.join(outlet_dir, 'Bills'))
        pdf.output(pdf_output_path)

        # Generate the Excel file for sales data
        sales_data = []
        for dish in dishes:
            sales_data.append({
                'Date': date,
                'Item': dish['name'],
                'Price': dish['price']
            })

        if add_ons:
            for add_on in add_ons:
                sales_data.append({
                    'Date': date,
                    'Item': add_on['name'],
                    'Price': add_on['qty'] * add_on['price']
                })

        sales_df = pd.DataFrame(sales_data)
        sales_folder = 'data/Sales'
        if not os.path.exists(sales_folder):
            os.makedirs(sales_folder)
        excel_filename = f"{date}_ON-{outlet}_ST-{subtotal:.2f}_D-{discount_amount:.2f}_T-{total_tax_amount:.2f}_FS-{final_subtotal:.2f}.xlsx"
        sales_df.to_excel(os.path.join(sales_folder, excel_filename), index=False)

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
                for add_on in add_ons:
                    pdf.cell(0, 5, txt=f"Add Ons: {add_on['name']}: {add_on['qty']} {add_on['unit']}", ln=True, align="L")

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

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs')
def raw_material_costs():
    return render_template('sales_management/raw_material_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs')
def procurement_costs():
    return render_template('sales_management/procurement_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs/submit', methods=['POST'])
def submit_raw_material_costs():
    file = request.files['file']
    date = request.form['date']
    if not file or not date:
        return jsonify({'success': False, 'message': 'File and date are required'})

    submitted_df = pd.read_excel(file)
    submitted_df['Quantity (Gm)'] = (pd.to_numeric(submitted_df['Quantity (Gm)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Quantity (Pieces)'] = (pd.to_numeric(submitted_df['Quantity (Pieces)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Unit Cost'] = (pd.to_numeric(submitted_df['Unit Cost'], errors='coerce').fillna(0)).round(2)

    submitted_df['Date'] = date
    submitted_df['Total Cost'] = (submitted_df['Unit Cost'] * (submitted_df['Quantity (Gm)'] + submitted_df['Quantity (Pieces)'])).round(2)

    table_html = submitted_df.to_html(index=False, classes='table table-striped')
    subtotal = round(submitted_df['Total Cost'].sum(), 2)

    return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal, 'data': submitted_df.to_dict(orient='records')})

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs/update', methods=['POST'])
def update_raw_material_costs():
    data = request.get_json()
    date = data['date']
    if not date:
        return jsonify({'success': False, 'message': 'Date is required'})

    # Extract the month from the date
    month = datetime.strptime(date, '%Y-%m-%d').strftime('%B-%Y')
    folder_path = os.path.join('data', 'Procurement Costs', 'Raw material', month)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'Raw_Material_Costs_{datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b-%Y")}.xlsx')

    # Save the submitted data as Excel file
    submitted_df = pd.DataFrame(data['data'])
    submitted_df.to_excel(file_path, index=False)

    return jsonify({'success': True, 'message': 'Cost table updated successfully'})

@sales_management_bp.route('/order-management/download_sample_form')
def download_sample_form():
    return send_file('data/Sample_Form.xlsx', as_attachment=True)

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs/see-data', methods=['GET'])
def see_raw_material_data():
    return render_template('sales_management/see_raw_material_data.html')

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs/get-data', methods=['POST'])
def get_raw_material_data():
    time_frame = request.form['time_frame']
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    folder_path = os.path.join('data', 'Procurement Costs', 'Raw material')
    all_files = []

    # Logic to determine the files to read based on the time frame
    if time_frame == 'Today':
        target_date = datetime.today().strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'Yesterday':
        target_date = (datetime.today() - timedelta(days=1)).strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'This Week':
        start_date = (datetime.today() - timedelta(days=datetime.today().weekday())).strftime('%Y-%m-%d')
        end_date = (datetime.today() + timedelta(days=6 - datetime.today().weekday())).strftime('%Y-%m-%d')
    elif time_frame == 'This Month':
        start_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        end_date = (datetime.today().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
    elif time_frame == 'Last Month':
        first = datetime.today().replace(day=1)
        last_month_end = first - timedelta(days=1)
        start_date = last_month_end.replace(day=1).strftime('%Y-%m-%d')
        end_date = last_month_end.strftime('%Y-%m-%d')
    elif time_frame == 'Last Three Months':
        start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
    elif time_frame == 'Choose Date':
        if not start_date or not end_date:
            return jsonify({'success': False, 'message': 'Start date and end date are required for chosen date range'})

    if start_date and end_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3].replace('.xlsx', ''), '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    if time_frame in ['Today', 'Yesterday'] or (time_frame == 'Choose Date' and (start_date == end_date)):
        table_html = final_df.to_html(index=False, classes='table table-striped')
        subtotal = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal})
    else:
        total_cost = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'total_cost': total_cost})

@sales_management_bp.route('/sales-management/procurement-costs/raw-material-costs/find-product-cost', methods=['POST'])
def find_product_cost():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    products = request.form['products']
    folder_path = os.path.join('data', 'Procurement Costs', 'Raw material')

    if not start_date or not end_date or not products:
        return jsonify({'success': False, 'message': 'Start date, end date, and products are required'})

    product_list = [p.strip() for p in products.split(',')]
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3].replace('.xlsx', ''), '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    product_costs = final_df[final_df['Product'].isin(product_list)].groupby('Product')['Total Cost'].sum().reset_index()

    if product_costs.empty:
        return jsonify({'success': False, 'message': 'No data found for the specified products'})

    product_costs['Total Cost'] = product_costs['Total Cost'].round(2)
    return jsonify({'success': True, 'product_costs': product_costs.to_dict(orient='records')})



@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs')
def packaging_material_costs():
    return render_template('sales_management/packaging_material_costs.html')


@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs/submit', methods=['POST'])
def submit_packaging_material_costs():
    file = request.files['file']
    date = request.form['date']
    if not file or not date:
        return jsonify({'success': False, 'message': 'File and date are required'})

    submitted_df = pd.read_excel(file)
    submitted_df['Quantity (Gm)'] = (pd.to_numeric(submitted_df['Quantity (Gm)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Quantity (Pieces)'] = (pd.to_numeric(submitted_df['Quantity (Pieces)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Unit Cost'] = (pd.to_numeric(submitted_df['Unit Cost'], errors='coerce').fillna(0)).round(2)

    submitted_df['Date'] = date
    submitted_df['Total Cost'] = (submitted_df['Unit Cost'] * (submitted_df['Quantity (Gm)'] + submitted_df['Quantity (Pieces)'])).round(2)

    table_html = submitted_df.to_html(index=False, classes='table table-striped')
    subtotal = round(submitted_df['Total Cost'].sum(), 2)

    return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal, 'data': submitted_df.to_dict(orient='records')})

@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs/update', methods=['POST'])
def update_packaging_material_costs():
    data = request.get_json()
    date = data['date']
    if not date:
        return jsonify({'success': False, 'message': 'Date is required'})

    # Extract the month from the date
    month = datetime.strptime(date, '%Y-%m-%d').strftime('%B-%Y')
    folder_path = os.path.join('data', 'Procurement Costs', 'Packaging material', month)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'Packaging_Material_Costs_{datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b-%Y")}.xlsx')

    # Save the submitted data as Excel file
    submitted_df = pd.DataFrame(data['data'])
    submitted_df.to_excel(file_path, index=False)

    return jsonify({'success': True, 'message': 'Cost table updated successfully'})

@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs/see-data', methods=['GET'])
def see_packaging_material_data():
    return render_template('sales_management/see_packaging_material_data.html')

@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs/get-data', methods=['POST'])
def get_packaging_material_data():
    time_frame = request.form['time_frame']
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    folder_path = os.path.join('data', 'Procurement Costs', 'Packaging material')
    all_files = []

    # Logic to determine the files to read based on the time frame
    if time_frame == 'Today':
        target_date = datetime.today().strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'Yesterday':
        target_date = (datetime.today() - timedelta(days=1)).strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'This Week':
        start_date = (datetime.today() - timedelta(days=datetime.today().weekday())).strftime('%Y-%m-%d')
        end_date = (datetime.today() + timedelta(days=6 - datetime.today().weekday())).strftime('%Y-%m-%d')
    elif time_frame == 'This Month':
        start_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        end_date = (datetime.today().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
    elif time_frame == 'Last Month':
        first = datetime.today().replace(day=1)
        last_month_end = first - timedelta(days=1)
        start_date = last_month_end.replace(day=1).strftime('%Y-%m-%d')
        end_date = last_month_end.strftime('%Y-%m-%d')
    elif time_frame == 'Last Three Months':
        start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
    elif time_frame == 'Choose Date':
        if not start_date or not end_date:
            return jsonify({'success': False, 'message': 'Start date and end date are required for chosen date range'})

    if start_date and end_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3], '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    if time_frame in ['Today', 'Yesterday'] or (time_frame == 'Choose Date' and (start_date == end_date)):
        table_html = final_df.to_html(index=False, classes='table table-striped')
        subtotal = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal})
    else:
        total_cost = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'total_cost': total_cost})

@sales_management_bp.route('/sales-management/procurement-costs/packaging-material-costs/find-product-cost', methods=['POST'])
def find_packaging_material_product_cost():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    products = request.form['products']
    folder_path = os.path.join('data', 'Procurement Costs', 'Packaging material')

    if not start_date or not end_date or not products:
        return jsonify({'success': False, 'message': 'Start date, end date, and products are required'})

    product_list = [p.strip() for p in products.split(',')]
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3], '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    product_costs = final_df[final_df['Product'].isin(product_list)].groupby('Product')['Total Cost'].sum().reset_index()

    if product_costs.empty:
        return jsonify({'success': False, 'message': 'No data found for the specified products'})

    product_costs['Total Cost'] = product_costs['Total Cost'].round(2)
    return jsonify({'success': True, 'product_costs': product_costs.to_dict(orient='records')})


@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs')
def outsourced_product_costs():
    return render_template('sales_management/outsourced_product_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs/submit', methods=['POST'])
def submit_outsourced_product_costs():
    file = request.files['file']
    date = request.form['date']
    if not file or not date:
        return jsonify({'success': False, 'message': 'File and date are required'})

    submitted_df = pd.read_excel(file)
    submitted_df['Quantity (Gm)'] = (pd.to_numeric(submitted_df['Quantity (Gm)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Quantity (Pieces)'] = (pd.to_numeric(submitted_df['Quantity (Pieces)'], errors='coerce').fillna(0)).round(2)
    submitted_df['Unit Cost'] = (pd.to_numeric(submitted_df['Unit Cost'], errors='coerce').fillna(0)).round(2)

    submitted_df['Date'] = date
    submitted_df['Total Cost'] = (submitted_df['Unit Cost'] * (submitted_df['Quantity (Gm)'] + submitted_df['Quantity (Pieces)'])).round(2)

    table_html = submitted_df.to_html(index=False, classes='table table-striped')
    subtotal = round(submitted_df['Total Cost'].sum(), 2)

    return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal, 'data': submitted_df.to_dict(orient='records')})

@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs/update', methods=['POST'])
def update_outsourced_product_costs():
    data = request.get_json()
    date = data['date']
    if not date:
        return jsonify({'success': False, 'message': 'Date is required'})

    # Extract the month from the date
    month = datetime.strptime(date, '%Y-%m-%d').strftime('%B-%Y')
    folder_path = os.path.join('data', 'Procurement Costs', 'Outsourced product', month)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'Outsourced_Product_Costs_{datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b-%Y")}.xlsx')

    # Save the submitted data as Excel file
    submitted_df = pd.DataFrame(data['data'])
    submitted_df.to_excel(file_path, index=False)

    return jsonify({'success': True, 'message': 'Cost table updated successfully'})

@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs/see-data', methods=['GET'])
def see_outsourced_product_data():
    return render_template('sales_management/see_outsourced_product_data.html')

@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs/get-data', methods=['POST'])
def get_outsourced_product_data():
    time_frame = request.form['time_frame']
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    folder_path = os.path.join('data', 'Procurement Costs', 'Outsourced product')
    all_files = []

    # Logic to determine the files to read based on the time frame
    if time_frame == 'Today':
        target_date = datetime.today().strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'Yesterday':
        target_date = (datetime.today() - timedelta(days=1)).strftime('%d-%b-%Y')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if target_date in name]
    elif time_frame == 'This Week':
        start_date = (datetime.today() - timedelta(days=datetime.today().weekday())).strftime('%Y-%m-%d')
        end_date = (datetime.today() + timedelta(days=6 - datetime.today().weekday())).strftime('%Y-%m-%d')
    elif time_frame == 'This Month':
        start_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        end_date = (datetime.today().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
    elif time_frame == 'Last Month':
        first = datetime.today().replace(day=1)
        last_month_end = first - timedelta(days=1)
        start_date = last_month_end.replace(day=1).strftime('%Y-%m-%d')
        end_date = last_month_end.strftime('%Y-%m-%d')
    elif time_frame == 'Last Three Months':
        start_date = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')
    elif time_frame == 'Choose Date':
        if not start_date or not end_date:
            return jsonify({'success': False, 'message': 'Start date and end date are required for chosen date range'})

    if start_date and end_date:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3], '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    if time_frame in ['Today', 'Yesterday'] or (time_frame == 'Choose Date' and (start_date == end_date)):
        table_html = final_df.to_html(index=False, classes='table table-striped')
        subtotal = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'table_html': table_html, 'subtotal': subtotal})
    else:
        total_cost = round(final_df['Total Cost'].sum(), 2)
        return jsonify({'success': True, 'total_cost': total_cost})

@sales_management_bp.route('/sales-management/procurement-costs/outsourced-product-costs/find-product-cost', methods=['POST'])
def find_outsourced_product_cost():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    products = request.form['products']
    folder_path = os.path.join('data', 'Procurement Costs', 'Outsourced product')

    if not start_date or not end_date or not products:
        return jsonify({'success': False, 'message': 'Start date, end date, and products are required'})

    product_list = [p.strip() for p in products.split(',')]
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    all_files = [os.path.join(root, name) for root, dirs, files in os.walk(folder_path) for name in files if start_date_dt <= datetime.strptime(name.split('_')[3], '%d-%b-%Y') <= end_date_dt]

    if not all_files:
        return jsonify({'success': False, 'message': 'No data found'})

    all_data = []
    for file in all_files:
        df = pd.read_excel(file)
        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)
    product_costs = final_df[final_df['Product'].isin(product_list)].groupby('Product')['Total Cost'].sum().reset_index()

    if product_costs.empty:
        return jsonify({'success': False, 'message': 'No data found for the specified products'})

    product_costs['Total Cost'] = product_costs['Total Cost'].round(2)
    return jsonify({'success': True, 'product_costs': product_costs.to_dict(orient='records')})



@sales_management_bp.route('/sales-management/procurement-costs/electricity-costs')
def electricity_costs():
    return render_template('sales_management/electricity_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/rental-costs')
def rental_costs():
    return render_template('sales_management/rental_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/salary-costs')
def salary_costs():
    return render_template('sales_management/salary_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/experiment-costs')
def experiment_costs():
    return render_template('sales_management/experiment_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/logistic-costs')
def logistic_costs():
    return render_template('sales_management/logistic_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/staff-food-costs')
def staff_food_costs():
    return render_template('sales_management/staff_food_costs.html')

@sales_management_bp.route('/sales-management/procurement-costs/miscellaneous-costs')
def miscellaneous_costs():
    return render_template('sales_management/miscellaneous_costs.html')
