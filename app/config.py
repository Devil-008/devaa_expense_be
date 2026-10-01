import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://expense_user:password@localhost:3306/expense_tracker')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Additional config options can be added here
