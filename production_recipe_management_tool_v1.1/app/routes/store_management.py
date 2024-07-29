 
from flask import Blueprint, render_template

store_management_bp = Blueprint('store_management_bp', __name__)

@store_management_bp.route('/store-management')
def store_management():
    return render_template('store_management/store_management.html')
