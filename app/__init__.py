from flask import Flask
from .config import Config
from .extensions import db, migrate, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Allow all for now, restrict in production

    # Register Blueprints
    from .models import User, Category, Transaction, Budget
    from .routes import auth, categories, transactions, dashboard
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(dashboard.bp)
    
    @app.route("/api/health")
    def health_check():
        return {"status": "ok"}

    return app
