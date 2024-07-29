import os
import sys
from flask import Flask, render_template
from app.routes.instruction_manual_generator import instruction_manual_generator_bp
# Add the parent directory of app to the system path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.routes import register_blueprints

app = Flask(__name__, template_folder='templates', static_folder='static')

# Register blueprints
register_blueprints(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
