from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import os

inventory_management_bp = Blueprint('inventory_management_bp', __name__)

@inventory_management_bp.route('/inventory-management')
def inventory_management():
    return render_template('inventory_management/inventory_management.html')

@inventory_management_bp.route('/raw-materials-dashboard', methods=['GET'])
def raw_materials_dashboard():
    try:
        data = pd.read_excel('data/Raw_Material_List.xlsx')
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(products=products)
        else:
            return render_template('inventory_management/inventory_management_raw_materials.html', products=products)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/update-raw-materials', methods=['POST'])
def update_raw_materials():
    try:
        updated_data = request.json['products']
        df = pd.DataFrame(updated_data)

        # Ensure the columns are in the correct order
        column_order = ['Product', 'Unit', 'Unit Cost', 'Current Stock (gm)', 'Current Stock (Pieces)']
        df = df[column_order]

        # Backup the previous file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'data/Raw_Material_List_BackUps/Raw_Material_List_{timestamp}.xlsx'
        os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
        os.rename('data/Raw_Material_List.xlsx', backup_filename)

        # Save the new data
        df.to_excel('data/Raw_Material_List.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/set-raw-materials-thresholds', methods=['POST'])
def set_raw_materials_thresholds():
    try:
        thresholds = request.json
        threshold_gm = float(thresholds['thresholdGm'])
        threshold_pieces = float(thresholds['thresholdPieces'])
        data = pd.read_excel('data/Raw_Material_List.xlsx')

        def check_threshold(row):
            current_stock_gm = row['Current Stock (gm)'] if pd.notna(row['Current Stock (gm)']) else float('inf')
            current_stock_pieces = row['Current Stock (Pieces)'] if pd.notna(row['Current Stock (Pieces)']) else float('inf')
            if row['Unit'] == 'gm':
                return current_stock_gm < threshold_gm
            else:
                return current_stock_pieces < threshold_pieces

        data['Below Threshold'] = data.apply(check_threshold, axis=1)
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/add-raw-material', methods=['POST'])
def add_raw_material():
    try:
        new_product = request.json
        df = pd.read_excel('data/Raw_Material_List.xlsx')
        new_product_df = pd.DataFrame([new_product])
        df = pd.concat([df, new_product_df], ignore_index=True)
        df.to_excel('data/Raw_Material_List.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/packaging-materials-dashboard', methods=['GET'])
def packaging_materials_dashboard():
    try:
        data = pd.read_excel('data/Packaging_Material_List.xlsx')
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(products=products)
        else:
            return render_template('inventory_management/inventory_management_packaging_materials.html', products=products)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/update-packaging-materials', methods=['POST'])
def update_packaging_materials():
    try:
        updated_data = request.json['products']
        df = pd.DataFrame(updated_data)

        # Ensure the columns are in the correct order
        column_order = ['Product', 'Unit', 'Unit Cost', 'Current Stock (gm)', 'Current Stock (Pieces)']
        df = df[column_order]

        # Backup the previous file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'data/Packaging_Material_List_BackUps/Packaging_Material_List_{timestamp}.xlsx'
        os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
        os.rename('data/Packaging_Material_List.xlsx', backup_filename)

        # Save the new data
        df.to_excel('data/Packaging_Material_List.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/set-packaging-materials-thresholds', methods=['POST'])
def set_packaging_materials_thresholds():
    try:
        thresholds = request.json
        threshold_gm = float(thresholds['thresholdGm']) if thresholds['thresholdGm'] is not None else float('inf')
        threshold_pieces = float(thresholds['thresholdPieces']) if thresholds['thresholdPieces'] is not None else float('inf')
        data = pd.read_excel('data/Packaging_Material_List.xlsx')

        def check_threshold(row):
            current_stock_gm = row['Current Stock (gm)'] if pd.notna(row['Current Stock (gm)']) else float('inf')
            current_stock_pieces = row['Current Stock (Pieces)'] if pd.notna(row['Current Stock (Pieces)']) else float('inf')
            if row['Unit'] == 'gm':
                return current_stock_gm < threshold_gm
            else:
                return current_stock_pieces < threshold_pieces

        data['Below Threshold'] = data.apply(check_threshold, axis=1)
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/own-production-dashboard', methods=['GET'])
def own_production_dashboard():
    try:
        data = pd.read_excel('data/Own_Production_Products_List.xlsx')
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(products=products)
        else:
            return render_template('inventory_management/inventory_management_own_production.html', products=products)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/outsourced-products-dashboard', methods=['GET'])
def outsourced_products_dashboard():
    try:
        data = pd.read_excel('data/Outsourced_Product_Lits.xlsx')
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(products=products)
        else:
            return render_template('inventory_management/inventory_management_outsourced_products.html', products=products)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/update-outsourced-products', methods=['POST'])
def update_outsourced_products():
    try:
        updated_data = request.json['products']
        df = pd.DataFrame(updated_data)

        # Ensure the columns are in the correct order
        column_order = ['Product', 'Unit', 'Unit Cost', 'Current Stock (gm)', 'Current Stock (Pieces)', 'Vendor', 'Vendor Phone Number']
        df = df[column_order]

        # Backup the previous file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'data/Outsourced_Product_Lits_BackUps/Outsourced_Product_Lits_{timestamp}.xlsx'
        os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
        os.rename('data/Outsourced_Product_Lits.xlsx', backup_filename)

        # Save the new data
        df.to_excel('data/Outsourced_Product_Lits.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/add-packaging-product', methods=['POST'])
def add_packaging_product():
    try:
        new_product = request.json
        df = pd.read_excel('data/Packaging_Material_List.xlsx')
        new_product_df = pd.DataFrame([new_product])
        df = pd.concat([df, new_product_df], ignore_index=True)
        df.to_excel('data/Packaging_Material_List.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@inventory_management_bp.route('/set-thresholds', methods=['POST'])
def set_thresholds():
    try:
        thresholds = request.json
        threshold_gm = float(thresholds['thresholdGm'])
        threshold_pieces = float(thresholds['thresholdPieces'])
        data = pd.read_excel('data/Outsourced_Product_Lits.xlsx')

        def check_threshold(row):
            current_stock_gm = row['Current Stock (gm)'] if pd.notna(row['Current Stock (gm)']) else float('inf')
            current_stock_pieces = row['Current Stock (Pieces)'] if pd.notna(row['Current Stock (Pieces)']) else float('inf')
            if row['Unit'] == 'gm':
                return current_stock_gm < threshold_gm
            else:
                return current_stock_pieces < threshold_pieces

        data['Below Threshold'] = data.apply(check_threshold, axis=1)
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/add-product', methods=['POST'])
def add_product():
    try:
        new_product = request.json
        df = pd.read_excel('data/Outsourced_Product_Lits.xlsx')
        new_product_df = pd.DataFrame([new_product])
        df = pd.concat([df, new_product_df], ignore_index=True)
        df.to_excel('data/Outsourced_Product_Lits.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/update-own-production-products', methods=['POST'])
def update_own_production_products():
    try:
        updated_data = request.json['products']
        df = pd.DataFrame(updated_data)

        # Ensure the columns are in the correct order
        column_order = ['Product', 'Unit', 'Unit Cost', 'Current Stock (gm)', 'Current Stock (Pieces)']
        df = df[column_order]

        # Backup the previous file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'data/Own_Production_Products_List_BackUps/Own_Production_Products_List_{timestamp}.xlsx'
        os.makedirs(os.path.dirname(backup_filename), exist_ok=True)
        os.rename('data/Own_Production_Products_List.xlsx', backup_filename)

        # Save the new data
        df.to_excel('data/Own_Production_Products_List.xlsx', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@inventory_management_bp.route('/set-own-production-thresholds', methods=['POST'])
def set_own_production_thresholds():
    try:
        thresholds = request.json
        threshold_gm = float(thresholds['thresholdGm'])
        threshold_pieces = float(thresholds['thresholdPieces'])
        data = pd.read_excel('data/Own_Production_Products_List.xlsx')

        def check_threshold(row):
            current_stock_gm = row['Current Stock (gm)'] if pd.notna(row['Current Stock (gm)']) else float('inf')
            current_stock_pieces = row['Current Stock (Pieces)'] if pd.notna(row['Current Stock (Pieces)']) else float('inf')
            if row['Unit'] == 'gm':
                return current_stock_gm < threshold_gm
            else:
                return current_stock_pieces < threshold_pieces

        data['Below Threshold'] = data.apply(check_threshold, axis=1)
        data = data.replace({np.nan: None})  # Replace NaN with None for JSON serialization
        products = data.to_dict(orient='records')
        return jsonify({'status': 'success', 'products': products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
