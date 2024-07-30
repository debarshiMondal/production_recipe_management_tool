# app/routes/instruction_manual_generator.py

from flask import Blueprint, request, jsonify, render_template, send_file, make_response
import os
import pandas as pd

CATEGORY_FILE_PATH = os.path.join('data', 'Category.txt')
OUR_PRODUCTION_PRODUCTS_UNIT_COST = 'data/Unit_Cost/Our_Production_Products_Unit_Cost.xlsx'
OUTSOURCED_PRODUCTS_UNIT_COST = 'data/Unit_Cost/Outsourced_Products_Unit_Cost.xlsx'
OUTSOURCED_PRODUCT_LIST = 'data/Outsourced_Product_Lits.xlsx'
RAW_MATERIAL_LIST = 'data/Raw_Material_List.xlsx'
PACKAGING_MATERIAL_LIST = 'data/Packaging_Material_List.xlsx'
OWN_PRODUCTION_PRODUCTS_LIST = 'data/Own_Production_Products_List.xlsx'

instruction_manual_generator_bp = Blueprint('instruction_manual_generator', __name__)

@instruction_manual_generator_bp.route('/instruction-manual-generator', methods=['GET'])
def instruction_manual_generator():
    return render_template('instruction_manual_generator/instruction_manual_generator.html')

@instruction_manual_generator_bp.route('/instruction-manual-generator/cooking-methods', methods=['GET'])
def cooking_methods():
    return "Cooking Methods Page"

@instruction_manual_generator_bp.route('/instruction-manual-generator/price-setting')
def price_setting():
    with open(CATEGORY_FILE_PATH, 'r') as file:
        categories = file.read().splitlines()
    return render_template('instruction_manual_generator/price_setting.html', categories=categories)

def read_categories():
    if os.path.exists(CATEGORY_FILE_PATH):
        with open(CATEGORY_FILE_PATH, 'r') as file:
            categories = file.read().splitlines()
        return categories
    return []

def write_category(category_name):
    with open(CATEGORY_FILE_PATH, 'a') as file:
        file.write(category_name + '\n')

def delete_category(category_name):
    categories = read_categories()
    categories = [category for category in categories if category != category_name]
    with open(CATEGORY_FILE_PATH, 'w') as file:
        for category in categories:
            file.write(category + '\n')

@instruction_manual_generator_bp.route('/instruction-manual-generator/create-category', methods=['POST'])
def create_category():
    data = request.get_json()
    category_name = data.get('category_name')
    if category_name:
        categories = read_categories()
        if category_name not in categories:
            write_category(category_name)
            categories.append(category_name)
            return jsonify(success=True, categories=categories)
    return jsonify(success=False)

@instruction_manual_generator_bp.route('/instruction-manual-generator/delete-category', methods=['POST'])
def delete_category_route():
    data = request.get_json()
    category_name = data.get('category_name')
    if category_name:
        delete_category(category_name)
        categories = read_categories()
        return jsonify(success=True, categories=categories)
    return jsonify(success=False)

@instruction_manual_generator_bp.route('/instruction-manual-generator/create-database', methods=['POST'])
def create_database():
    try:
        # Step 1: Populate Our_Production_Products_Unit_Cost
        recipes_path = 'data/Recipes'
        production_data = []
        invalid_files = []

        for recipe_file in os.listdir(recipes_path):
            if recipe_file.endswith('.xlsx'):
                file_name_parts = recipe_file.split('_')
                if is_invalid_number(file_name_parts[0]):
                    invalid_files.append(recipe_file)
                    print(f"Invalid file detected: {recipe_file} (does not start with a number)")
                    continue

                try:
                    recipe_df = pd.read_excel(os.path.join(recipes_path, recipe_file))
                    total_cost = recipe_df['Price'].sum()
                    original_quantity = int(file_name_parts[0])  # Assuming file name starts with quantity
                    unit_cost = total_cost / original_quantity
                    unit = file_name_parts[1]
                    product_name = ' '.join(file_name_parts[2:]).replace('.xlsx', '')
                    production_data.append([product_name, unit, unit_cost])
                except Exception as e:
                    invalid_files.append(recipe_file)
                    print(f"Error processing file {recipe_file}: {e}")
                    continue

        if invalid_files:
            error_message = f"Invalid recipe files in /data/Recipes: {', '.join(invalid_files)}"
            print(error_message)
            return jsonify({'success': False, 'error': error_message})

        production_df = pd.DataFrame(production_data, columns=['Product', 'Unit', 'Unit Cost'])
        production_df.to_excel(OUR_PRODUCTION_PRODUCTS_UNIT_COST, index=False)
    
        # Step 2: Update Outsourced_Products_Unit_Cost
        outsourced_product_list_df = pd.read_excel(OUTSOURCED_PRODUCT_LIST)
        outsourced_product_unit_cost_df = outsourced_product_list_df[['Product', 'Unit', 'Unit Cost']]
        outsourced_product_unit_cost_df.to_excel(OUTSOURCED_PRODUCTS_UNIT_COST, index=False)
        
        # Step 3: Update Own_Production_Products_List
        own_production_products_list_df = pd.read_excel(OWN_PRODUCTION_PRODUCTS_LIST)

        # Remove products that no longer exist in Our_Production_Products_Unit_Cost.xlsx
        existing_products = production_df['Product'].values
        own_production_products_list_df = own_production_products_list_df[own_production_products_list_df['Product'].isin(existing_products)]

        # Update or add new products
        for index, row in production_df.iterrows():
            product_name = row['Product']
            if product_name in own_production_products_list_df['Product'].values:
                own_production_products_list_df.loc[own_production_products_list_df['Product'] == product_name, ['Unit', 'Unit Cost']] = row['Unit'], row['Unit Cost']
            else:
                new_row = pd.DataFrame([[product_name, row['Unit'], row['Unit Cost'], 0, 0]], columns=own_production_products_list_df.columns)
                own_production_products_list_df = pd.concat([own_production_products_list_df, new_row], ignore_index=True)

        own_production_products_list_df.to_excel(OWN_PRODUCTION_PRODUCTS_LIST, index=False)

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def is_invalid_number(s):
    try:
        int(s)
        return False
    except ValueError:
        return True

@instruction_manual_generator_bp.route('/instruction-manual-generator/create-dish', methods=['GET'])
def create_dish():
    dish_name = request.args.get('dish_name', '')
    with open(CATEGORY_FILE_PATH, 'r') as file:
        categories = file.read().splitlines()
    return render_template('instruction_manual_generator/instruction_manual_generator_create_dish.html', dish_name=dish_name, categories=categories)

@instruction_manual_generator_bp.route('/instruction-manual-generator/get-ingredients', methods=['GET'])
def get_ingredients():
    category = request.args.get('category', '')
    ingredients = []

    # Load ingredients from both production and outsourced files
    for file_path in [OUR_PRODUCTION_PRODUCTS_UNIT_COST, OUTSOURCED_PRODUCTS_UNIT_COST]:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            filtered_ingredients = df[df['Product'].str.contains(category, case=False, na=False)]['Product'].tolist()
            print(f"Ingredients for {category} from {file_path}: {filtered_ingredients}")  # Debugging line
            ingredients.extend(filtered_ingredients)

    print(f"Final ingredients for {category}: {ingredients}")  # Debugging line
    return jsonify({'ingredients': ingredients})

@instruction_manual_generator_bp.route('/instruction-manual-generator/get-categories-and-products', methods=['GET'])
def get_categories_and_products():
    try:
        categories = read_categories()
        products = {category: [] for category in categories}

        # Read products from Our_Production_Products_Unit_Cost.xlsx
        our_production_df = pd.read_excel(OUR_PRODUCTION_PRODUCTS_UNIT_COST)
        for category in categories:
            filtered_products = our_production_df[our_production_df['Product'].str.contains(category, case=False)]
            products[category].extend(filtered_products['Product'])

        # Read products from Outsourced_Products_Unit_Cost.xlsx
        outsourced_df = pd.read_excel(OUTSOURCED_PRODUCTS_UNIT_COST)
        for category in categories:
            filtered_products = outsourced_df[outsourced_df['Product'].str.contains(category, case=False)]
            products[category].extend(filtered_products['Product'])

        return jsonify({'success': True, 'categories': categories, 'products': products})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@instruction_manual_generator_bp.route('/instruction-manual-generator/get-unit-cost', methods=['GET'])
def get_unit_cost():
    product = request.args.get('product', '')
    unit_cost = None

    # Load unit cost from both production and outsourced files
    for file_path in [OUR_PRODUCTION_PRODUCTS_UNIT_COST, OUTSOURCED_PRODUCTS_UNIT_COST, RAW_MATERIAL_LIST, PACKAGING_MATERIAL_LIST]:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            filtered_product = df[df['Product'] == product]
            if not filtered_product.empty:
                unit_cost = filtered_product.iloc[0]['Unit Cost']
                break

    if unit_cost is not None:
        return jsonify({'unitCost': unit_cost})
    else:
        return jsonify({'error': 'Product not found'}), 404

@instruction_manual_generator_bp.route('/instruction-manual-generator/get-raw-materials', methods=['GET'])
def get_raw_materials():
    raw_materials = []
    if os.path.exists(RAW_MATERIAL_LIST):
        df = pd.read_excel(RAW_MATERIAL_LIST)
        raw_materials = df['Product'].tolist()
        return jsonify({'rawMaterials': raw_materials})
    else:
        return jsonify({'error': 'Raw materials file not found'}), 404

@instruction_manual_generator_bp.route('/instruction-manual-generator/get-packaging-materials', methods=['GET'])
def get_packaging_materials():
    packaging_materials = []
    if os.path.exists(PACKAGING_MATERIAL_LIST):
        df = pd.read_excel(PACKAGING_MATERIAL_LIST)
        packaging_materials = df['Product'].tolist()
        return jsonify({'packagingMaterials': packaging_materials})
    else:
        return jsonify({'error': 'Raw materials file not found'}), 404

@instruction_manual_generator_bp.route('/download-ingredients/<dish_name>', methods=['GET'])
def download_ingredients(dish_name):
    # Generate the content of the ingredients file
    # Here you should retrieve the actual ingredients and quantities for the dish
    # For demonstration purposes, I'm using placeholder content
    content = f"Ingredients for {dish_name}\n- Ingredient 1: 100g\n- Ingredient 2: 200ml\n"
    response = make_response(content)
    response.headers["Content-Disposition"] = f"attachment; filename={dish_name}_ingredients.txt"
    response.headers["Content-Type"] = "text/plain"
    return response
