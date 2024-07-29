# File: production_recipe_management_tool_v1.0/main_routes.py
from flask import Flask, render_template
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    print("Current directory:", os.getcwd())  # Print the current working directory
    template_path = os.path.join(app.template_folder, 'index.html')
    print("Template folder path:", app.template_folder)  # Print the template folder path
    print("Index template exists:", os.path.exists(template_path))  # Check if index.html exists
    print("Index template path:", template_path)
    return render_template('index.html')

@app.route('/recipe-management')
def recipe_management():
    return render_template('recipe_management/recipe_management.html')

@app.route('/inventory-management')
def inventory_management():
    return render_template('inventory_management/inventory_management.html')

@app.route('/order-management')
def order_management():
    return render_template('order_management/order_management.html')

@app.route('/sales-management')
def sales_management():
    return render_template('sales_management/sales_management.html')

@app.route('/store-management')
def store_management():
    return render_template('store_management/store_management.html')

@app.route('/instruction-manual-generator')
def instruction_manual_generator():
    return render_template('instruction_manual_generator/instruction_manual_generator.html')
