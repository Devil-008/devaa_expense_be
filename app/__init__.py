from flask import Flask
from flask_cors import CORS
from .extensions import db
from .routes import auth, categories, transactions, dashboard, reports

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(reports.reports_bp)
    return app