from flask import Flask, redirect, url_for
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    # Import routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.tracker import tracker_bp
    app.register_blueprint(tracker_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.coupon import coupons_bp
    app.register_blueprint(coupons_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.admin_mod.users import admin_users_bp
    app.register_blueprint(admin_users_bp)

    from app.routes.admin_mod.scan import admin_scan_bp
    app.register_blueprint(admin_scan_bp)

    # Redirect root URL to /dashboard
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.home'))

    return app