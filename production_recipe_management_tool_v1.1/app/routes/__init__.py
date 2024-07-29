 
from flask import Blueprint
from .recipe_management import recipe_management_bp
from .inventory_management import inventory_management_bp
from .order_management import order_management_bp
from .sales_management import sales_management_bp
from .store_management import store_management_bp
from .instruction_manual_generator import instruction_manual_generator_bp

# Create a list of all blueprints
all_blueprints = [
    recipe_management_bp,
    inventory_management_bp,
    order_management_bp,
    sales_management_bp,
    store_management_bp,
    instruction_manual_generator_bp
]

def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    for bp in all_blueprints:
        app.register_blueprint(bp)
