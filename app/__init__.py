from flask import Flask
from .config import Config
from .extensions import db, migrate, cors
from .utils.responses import api_response

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    from .routes import auth, categories, transactions, dashboard
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(dashboard.bp)

    @app.errorhandler(404)
    def not_found(e):
        return api_response(404, False, "Resource not found", None)

    @app.errorhandler(500)
    def server_error(e):
        return api_response(500, False, "Internal server error", None)

    return app