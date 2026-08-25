from flask import Flask, jsonify
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config
from .db import Database

login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "60 per hour"])


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)
    db = Database(app.config["DATABASE_PATH"])
    db.initialize()
    db.bootstrap_admin(app.config.get("BOOTSTRAP_ADMIN_EMAIL"), app.config.get("BOOTSTRAP_ADMIN_PASSWORD"))
    app.extensions["vexpanel_db"] = db

    login_manager.init_app(app)
    limiter.init_app(app)

    from .auth import load_user
    login_manager.user_loader(load_user)

    from .api.auth import auth_api
    from .api.vps import vps_api
    from .api.admin import admin_api
    app.register_blueprint(auth_api, url_prefix="/api/v1/auth")
    app.register_blueprint(vps_api, url_prefix="/api/v1/vps")
    app.register_blueprint(admin_api, url_prefix="/api/v1/admin")

    @app.get("/health")
    def health():
        return jsonify(success=True, data={"service": "vexpanel", "status": "ok"})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(success=False, error={"code": "NOT_FOUND", "message": "Resource not found."}), 404

    return app
