import os
from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .extensions import db, migrate, login_manager, csrf


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"), static_folder=os.path.join(os.getcwd(), "static"))
    app.config.from_object(Config())

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Import models so migrations can discover them
    from . import models  # noqa: F401

    # Blueprints
    from .auth import auth_bp
    from .admin import admin_bp
    from .employee import employee_bp
    from .manager import manager_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(manager_bp, url_prefix="/manager")

    # Create DB tables for first run (mostly for SQLite/local dev)
    with app.app_context():
        db.create_all()

    return app
