from flask import Flask, redirect, url_for, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config
import os
from datetime import timedelta

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Security configurations
    app.config['SESSION_COOKIE_SECURE'] = True if not app.debug else False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # CSRF protection
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = True if not app.debug else False

    # Extensions initialization
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)


    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'

    # Blueprint registration
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.student import student as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/student')

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Jinja2 filters
    @app.template_filter('turkish_day')
    def turkish_day(day):
        """Convert English day names to Turkish"""
        day_map = {
            'monday': 'Pazartesi',
            'tuesday': 'Salı',
            'wednesday': 'Çarşamba',
            'thursday': 'Perşembe',
            'friday': 'Cuma',
            'saturday': 'Cumartesi',
            'sunday': 'Pazar'
        }
        return day_map.get(day.lower(), day)

    # Error handlers
    register_error_handlers(app)

    # Ana sayfa route'u
    @app.route('/')
    def index():
        from flask_login import current_user
        
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            return render_template('index.html')

    # Create database tables and default admin user
    with app.app_context():
        db.create_all()
        create_default_admin()

    return app

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500



def create_default_admin():
    """Create default admin user if it doesn't exist"""
    from app.models.user import User

    try:
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@admin.com').first()

        if not admin_user:
            # Create default admin user
            admin_user = User(
                email='admin@admin.com',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')

            db.session.add(admin_user)
            db.session.commit()

            print("✅ Default admin user created successfully!")
            print("   Email: admin@admin.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Admin user already exists")

    except Exception as e:
        print(f"❌ Error creating default admin user: {e}")
        db.session.rollback() 