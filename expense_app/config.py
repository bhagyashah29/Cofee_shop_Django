import os
from dotenv import load_dotenv


def load_config(app):
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')

    # Database
    database_url = os.getenv('DATABASE_URL', 'sqlite:///instance/app.db')
    if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
        # Ensure absolute path for sqlite
        instance_path = app.instance_path
        os.makedirs(instance_path, exist_ok=True)
        db_path = database_url.replace('sqlite:///', '')
        database_url = f"sqlite:///{os.path.join(instance_path, os.path.basename(db_path))}"

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # External APIs
    app.config['REST_COUNTRIES_URL'] = os.getenv('REST_COUNTRIES_URL', 'https://restcountries.com/v3.1/all?fields=name,currencies')
    app.config['EXCHANGE_BASE_URL'] = os.getenv('EXCHANGE_BASE_URL', 'https://api.exchangerate-api.com/v4/latest')
    app.config['DEFAULT_COUNTRY'] = os.getenv('DEFAULT_COUNTRY', 'United States')

    # Uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
