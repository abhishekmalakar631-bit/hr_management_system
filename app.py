from flask import Flask, render_template, session
from config import Config
from db import init_db
import os

app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# ======================== Register Blueprints ========================
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.attendance import attendance_bp
from routes.leave import leave_bp
from routes.profile import profile_bp
from routes.salary import salary_bp
from routes.notifications import notifications_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(leave_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(salary_bp)
app.register_blueprint(notifications_bp)


# ======================== Landing Page ========================
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')


# ======================== Context Processor ========================
app.jinja_env.globals.update(hasattr=hasattr)


@app.context_processor
def inject_session():
    """Make session data available to all templates."""
    return {
        'current_user': {
            'user_id': session.get('user_id'),
            'employee_id': session.get('employee_id'),
            'emp_code': session.get('emp_code'),
            'email': session.get('email'),
            'role': session.get('role'),
            'first_name': session.get('first_name', ''),
            'last_name': session.get('last_name', ''),
            'is_authenticated': session.get('user_id') is not None,
            'is_hr': session.get('role') == 'hr_manager'
        }
    }


# ======================== Error Handlers ========================
@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('index.html'), 500


# ======================== Initialize & Run ========================
if __name__ == '__main__':
    print("Initializing HRMS Serene database...")
    init_db()
    app.run(debug=True)