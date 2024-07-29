from flask import Blueprint, render_template, request, redirect, url_for, send_file, jsonify
import os
import pandas as pd
from io import BytesIO
from app.utils.excel_operations import generate_shopping_list
from app.utils.pdf_operations import generate_estimation_pdf

scaled_recipe_memory = {}
recipe_management_bp = Blueprint('recipe_management_bp', __name__)

UPLOAD_FOLDER = 'data/Recipes'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_total_price(filepath):
    df = pd.read_excel(filepath)
    return df['Price'].sum()

@recipe_management_bp.route('/recipe-management')
def recipe_management():
    return render_template('recipe_management/recipe_management.html')

@recipe_management_bp.route('/recipe-management/add-update-delete')
def add_update_delete():
    recipes = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            try:
                parts = filename.rsplit('_', 2)
                if len(parts) == 3:
                    yield_value, unit, name_with_ext = parts
                    name = name_with_ext.rsplit('.', 1)[0]
                    total_price = calculate_total_price(filepath)
                    unit_cost = round(total_price / float(yield_value), 3)
                    unit_display = f"{unit_cost}/{unit[:-1].capitalize()}"
                    recipes.append({
                        'name': name,
                        'yield': f"{yield_value} {unit.capitalize()}",
                        'unit_cost': unit_display,
                        'filename': filename
                    })
            except ValueError as e:
                print(f"Error processing file {filename}: {e}")
    return render_template('recipe_management/add_update_delete.html', recipes=recipes)

@recipe_management_bp.route('/recipe-management/scale-ingredients')
def scale_ingredients():
    recipes = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            parts = filename.rsplit('_', 2)
            if len(parts) == 3:
                yield_value, unit, name_with_ext = parts
                name = name_with_ext.rsplit('.', 1)[0]
                recipes.append({
                    'name': name,
                    'filename': filename,
                    'yield': yield_value,
                    'unit': unit
                })
    return render_template('recipe_management/scale_ingredients.html', recipes=recipes)

@recipe_management_bp.route('/recipe-management/upload', methods=['POST'])
def upload_file():
    if 'fileUpload' not in request.files:
        return redirect(request.url)
    file = request.files['fileUpload']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        recipe_name = request.form['recipeName']
        unit = request.form['unit']
        yield_value = request.form['yield']
        filename = f"{yield_value}_{unit}_{recipe_name}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return redirect(url_for('recipe_management_bp.add_update_delete'))
    return redirect(request.url)

@recipe_management_bp.route('/recipe-management/delete/<filename>', methods=['GET'])
def delete_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('recipe_management_bp.add_update_delete'))

@recipe_management_bp.route('/recipe-management/generate-scaled-recipe', methods=['POST'])
def generate_scaled_recipe():
    data = request.json
    recipe = data['recipes'][0]
    filename = recipe['filename']
    unit = recipe['unit']
    quantity = float(recipe['quantity'])
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    df = pd.read_excel(filepath)
    
    # Calculate the scaling factor based on the original recipe yield
    original_yield = float(filename.split('_')[0])  # Extracting original yield from the filename
    scaling_factor = quantity / original_yield

    # Apply the scaling factor
    if 'Quantity (Gm)' in df.columns:
        df['Quantity (Gm)'] = df['Quantity (Gm)'] * scaling_factor
    if 'Quantity (Pieces)' in df.columns:
        df['Quantity (Pieces)'] = df['Quantity (Pieces)'] * scaling_factor

    # Remove 'Unit Cost' and 'Price' columns if they exist
    if 'Unit Cost' in df.columns:
        df = df.drop(columns=['Unit Cost'])
    if 'Price' in df.columns:
        df = df.drop(columns=['Price'])
    
    # Save scaled recipe temporarily in memory
    original_filename = os.path.basename(filepath).rsplit('.', 1)[0]
    recipe_name = original_filename.rsplit('_', 2)[2]
    scaled_filename = f"{quantity} {unit.capitalize()} {recipe_name} Recipe.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    # Temporarily save scaled recipe in memory for downloading
    scaled_recipe_memory[scaled_filename] = output.getvalue()

    return jsonify({
        'name': recipe_name,
        'quantity': quantity,
        'downloadLink': url_for('recipe_management_bp.download_scaled_recipe', filename=scaled_filename)
    })


@recipe_management_bp.route('/recipe-management/download-scaled-recipe/<filename>', methods=['GET'])
def download_scaled_recipe(filename):
    if filename not in scaled_recipe_memory:
        return jsonify({'error': 'File not found'}), 404

    output = BytesIO(scaled_recipe_memory[filename])
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@recipe_management_bp.route('/recipe-management/generate-shopping-list', methods=['POST'])
def generate_shopping_list_route():
    data = request.json
    recipes = data.get('recipes', [])
    
    try:
        shopping_list = generate_shopping_list(recipes)
        shopping_list_filepath = os.path.join(DOWNLOAD_FOLDER, f'shopping_list_{pd.Timestamp.now().strftime("%Y-%m-%d")}.xlsx')
        shopping_list.to_excel(shopping_list_filepath, index=False)
        return send_file(shopping_list_filepath, as_attachment=True, download_name=f'shopping_list_{pd.Timestamp.now().strftime("%Y-%m-%d")}.xlsx')
    except KeyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipe_management_bp.route('/recipe-management/generate-estimation', methods=['POST'])
def generate_estimation_route():
    data = request.json
    recipes = data.get('recipes', [])
    estimation_data = []

    for recipe in recipes:
        item = recipe['filename']  # Fetching the item name from the Palette section
        quantity = recipe['quantity']
        subtotal = recipe['subtotal']
        estimation_data.append({'Item': item, 'Quantity': quantity, 'Subtotal': subtotal})

    estimation_df = pd.DataFrame(estimation_data, columns=['Item', 'Quantity', 'Subtotal'])
    estimation_report = generate_estimation_pdf(estimation_df)
    
    return send_file(estimation_report, as_attachment=True, download_name=f'estimation_of_production_{pd.Timestamp.now().strftime("%Y-%m-%d")}.pdf')


@recipe_management_bp.route('/get-unit-cost', methods=['GET'])
def get_unit_cost():
    filename = request.args.get('filename')
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    df = pd.read_excel(filepath)
    total_price = df['Price'].sum()
    yield_value, unit, _ = filename.rsplit('_', 2)
    
    try:
        unit_cost = round(total_price / float(yield_value), 3)
    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'unit_cost': unit_cost})
