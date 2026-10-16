import os

class Config:
    # Secret Key for Sessions
    SECRET_KEY = os.environ.get("SECRET_KEY") or "smart_hospital_master_secret_2026"

    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "rawatpalak089")
    MYSQL_DB = os.environ.get("MYSQL_DB", "hospital_db")

    if MYSQL_PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads & Assets
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Session Security
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
