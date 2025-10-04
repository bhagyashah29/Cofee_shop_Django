from flask import Flask
from .extensions import db, migrate, login_manager
from .config import load_config


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    load_config(app)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprints
    from .blueprints.auth.views import auth_bp
    from .blueprints.admin.views import admin_bp
    from .blueprints.expenses.views import expenses_bp
    from .blueprints.approvals.views import approvals_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(approvals_bp, url_prefix='/approvals')

    @app.get('/')
    def index():
        return "Expense Reimbursement App - Flask"

    return app
