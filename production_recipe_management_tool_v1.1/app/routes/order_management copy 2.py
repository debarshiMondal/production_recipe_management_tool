from flask import Blueprint, render_template, request, jsonify, url_for, send_file
import os
import pandas as pd
from datetime import datetime

order_management_bp = Blueprint('order_management', __name__)

@order_management_bp.route('/order-management')
def order_management():
    return render_template('order_management/order_management.html')

@order_management_bp.route('/own_production_kot')
def own_production_kot():
    # Load data from Excel file
    df = pd.read_excel('data/Own_Production_Products_List.xlsx')
    products = df.to_dict(orient='records')
    return render_template('order_management/own_production_kot.html', products=products)

@order_management_bp.route('/outsourced_product_order_ticket')
def outsourced_product_order_ticket():
    # Load data from Excel file
    df = pd.read_excel('data/Outsourced_Product_Lits.xlsx')
    products = df.to_dict(orient='records')
    return render_template('order_management/outsourced_product_order_ticket.html', products=products)

@order_management_bp.route('/packaging_materials_shopping_list')
def packaging_materials_shopping_list():
    # Load data from Excel file
    df = pd.read_excel('data/Packaging_Material_List.xlsx')
    products = df.to_dict(orient='records')
    return render_template('order_management/packaging_materials_shopping_list.html', products=products)

@order_management_bp.route('/confirmed_purchase')
def confirmed_purchase():
    return render_template('order_management/confirmed_purchase.html')

@order_management_bp.route('/download_sample_form')
def download_sample_form():
    return send_file('data/Sample_Form.xlsx', as_attachment=True)

@order_management_bp.route('/submit_<material_type>_form', methods=['POST'])
def submit_form(material_type):
    file = request.files['file']
    if not file:
        return jsonify({'success': False, 'message': 'No file uploaded'})

    # Read the submitted form
    submitted_df = pd.read_excel(file)

    # Load the corresponding data file
    data_file_map = {
        'raw_material': 'data/Raw_Material_List.xlsx',
        'packaging_material': 'data/Packaging_Material_List.xlsx',
        'outsourced_products': 'data/Outsourced_Product_Lits.xlsx',
        'own_production': 'data/Own_Production_Products_List.xlsx'
    }

    data_df = pd.read_excel(data_file_map[material_type])

    # Process the data and generate the UI table
    comparison_results = []
    missing_products = []
    for _, submitted_row in submitted_df.iterrows():
        product = submitted_row['Product']
        quantity_gm = submitted_row.get('Quantity (Gm)', 0)
        quantity_pieces = submitted_row.get('Quantity (Pieces)', 0)
        unit_cost = submitted_row['Unit Cost']

        data_rows = data_df[data_df['Product'] == product]
        if data_rows.empty:
            missing_products.append(product)
            continue

        data_row = data_rows.iloc[0]
        current_stock = data_row['Current Stock (gm)'] if data_row['Unit'] == 'gm' else data_row['Current Stock (Pieces)']
        unit = data_row['Unit']
        required_quantity = quantity_gm if unit == 'gm' else quantity_pieces

        if required_quantity > current_stock:
            shopping_requirement = f"{required_quantity - current_stock} {unit}"
        else:
            shopping_requirement = "In stock"

        price = unit_cost * max(0, required_quantity - current_stock)

        comparison_results.append({
            'Product': product,
            'Unit Cost': unit_cost,
            'Unit': unit,
            'Current Stock': current_stock,
            'Shopping Requirement': shopping_requirement,
            'Price': price,
            'Vendor': data_row.get('Vendor', ''),
            'Vendor Phone Number': data_row.get('Vendor Phone Number', '')
        })

    results_df = pd.DataFrame(comparison_results)

    table_html = results_df.to_html(index=False, classes='comparison-table')

    if comparison_results:
        filename = f"{material_type.capitalize()}_Shopping_List_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join('downloads', filename)

        # Ensure the downloads directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results_df.to_excel(filepath, index=False)

        download_url = url_for('order_management.download_file', filename=filename)
        return jsonify({'success': True, 'table_html': table_html, 'download_url': download_url, 'missing_products': missing_products})
    else:
        return jsonify({'success': False, 'missing_products': missing_products})


@order_management_bp.route('/update_<material_type>_inventory', methods=['POST'])
def update_inventory_form(material_type):
    file = request.files['file']
    if not file:
        return jsonify({'success': False, 'message': 'No file uploaded'})

    # Read the submitted form
    submitted_df = pd.read_excel(file)

    # Load the corresponding data file
    data_file_map = {
        'raw_material': 'data/Raw_Material_List.xlsx',
        'packaging_material': 'data/Packaging_Material_List.xlsx',
        'outsourced_products': 'data/Outsourced_Product_Lits.xlsx',
        'own_production': 'data/Own_Production_Products_List.xlsx'
    }

    data_df = pd.read_excel(data_file_map[material_type])

    # Process the data and generate the UI table
    updated_results = []
    missing_products = []
    for _, submitted_row in submitted_df.iterrows():
        product = submitted_row['Product']
        quantity_gm = submitted_row.get('Quantity (Gm)', 0)
        quantity_pieces = submitted_row.get('Quantity (Pieces)', 0)

        data_rows = data_df[data_df['Product'] == product]
        if data_rows.empty:
            missing_products.append(product)
            continue

        data_index = data_rows.index[0]
        if data_df.at[data_index, 'Unit'] == 'gm':
            data_df.at[data_index, 'Current Stock (gm)'] += quantity_gm
        else:
            data_df.at[data_index, 'Current Stock (Pieces)'] += quantity_pieces

        updated_results.append(data_df.loc[data_index])

    results_df = pd.DataFrame(updated_results)

    table_html = results_df.to_html(index=False, classes='comparison-table')

    if updated_results:
        filename = f"{material_type.capitalize()}_Updated_Inventory_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join('downloads', filename)

        # Ensure the downloads directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        results_df.to_excel(filepath, index=False)

        # Save the updated data back to the original file
        data_df.to_excel(data_file_map[material_type], index=False)

        download_url = url_for('order_management.download_file', filename=filename)
        return jsonify({'success': True, 'table_html': table_html, 'download_url': download_url, 'missing_products': missing_products})
    else:
        return jsonify({'success': False, 'missing_products': missing_products})


@order_management_bp.route('/save_order_ticket', methods=['POST'])
def save_order_ticket():
    order_values = request.json
    updated_products = []

    # Load data from Excel file
    df = pd.read_excel('data/Outsourced_Product_Lits.xlsx')

    for index, row in df.iterrows():
        product_name = row['Product']
        order_key = f'order_value_{product_name}'
        if order_key in order_values and order_values[order_key]:
            updated_products.append({
                'Product': row['Product'],
                'Unit': row['Unit'],
                'Unit Cost': row['Unit Cost'],
                'Current Stock (gm)': row['Current Stock (gm)'],
                'Current Stock (Pieces)': row['Current Stock (Pieces)'],
                'Vendor': row['Vendor'],
                'Vendor Phone Number': row['Vendor Phone Number'],
                'Order_Value': order_values[order_key]
            })

    if updated_products:
        new_df = pd.DataFrame(updated_products)
        filename = f"Outsourced_Product_Order_Ticket_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join('downloads', filename)

        # Ensure the downloads directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        new_df.to_excel(filepath, index=False)

        return jsonify({'success': True, 'download_url': url_for('order_management.download_file', filename=filename)})
    else:
        return jsonify({'success': False})

@order_management_bp.route('/save_shopping_list', methods=['POST'])
def save_shopping_list():
    order_values = request.json
    updated_products = []

    # Load data from Excel file
    df = pd.read_excel('data/Packaging_Material_List.xlsx')

    for index, row in df.iterrows():
        product_name = row['Product']
        order_key = f'order_value_{product_name}'
        if order_key in order_values and order_values[order_key]:
            updated_products.append({
                'Product': row['Product'],
                'Unit': row['Unit'],
                'Unit Cost': row['Unit Cost'],
                'Current Stock (gm)': row['Current Stock (gm)'],
                'Current Stock (Pieces)': row['Current Stock (Pieces)'],
                'Order_Value': order_values[order_key]
            })

    if updated_products:
        new_df = pd.DataFrame(updated_products)
        filename = f"Packaging_Materials_Shopping_List_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join('downloads', filename)

        # Ensure the downloads directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        new_df.to_excel(filepath, index=False)

        return jsonify({'success': True, 'download_url': url_for('order_management.download_file', filename=filename)})
    else:
        return jsonify({'success': False})

@order_management_bp.route('/downloads/<filename>')
def download_file(filename):
    return send_file(os.path.join('downloads', filename), as_attachment=True)
