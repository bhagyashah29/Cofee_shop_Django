import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:////workspace/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # External APIs
    RESTCOUNTRIES_API_URL = os.getenv(
        "RESTCOUNTRIES_API_URL",
        "https://restcountries.com/v3.1/all?fields=name,currencies",
    )
    EXCHANGE_RATE_API_BASE_URL = os.getenv(
        "EXCHANGE_RATE_API_BASE_URL",
        "https://api.exchangerate-api.com/v4/latest",
    )

    # Uploads / OCR
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/workspace/uploads")
    MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", "10"))
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH_MB * 1024 * 1024
    OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
    TESSERACT_CMD = os.getenv("TESSERACT_CMD")
