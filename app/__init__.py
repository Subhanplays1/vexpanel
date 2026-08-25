from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
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

    from .auth import load_user, User
    login_manager.user_loader(load_user)

    from .api.auth import auth_api
    from .api.vps import vps_api
    from .api.admin import admin_api
    app.register_blueprint(auth_api, url_prefix="/api/v1/auth")
    app.register_blueprint(vps_api, url_prefix="/api/v1/vps")
    app.register_blueprint(admin_api, url_prefix="/api/v1/admin")

    @app.get("/")
    def index(): return redirect(url_for("dashboard") if current_user.is_authenticated else url_for("login"))

    @app.route("/login", methods=["GET", "POST"], endpoint="login")
    def login_page():
        if current_user.is_authenticated: return redirect(url_for("dashboard"))
        error = None
        if request.method == "POST":
            user = db.verify_user(request.form.get("username", ""), request.form.get("password", ""))
            if user: login_user(User(user)); return redirect(url_for("dashboard"))
            error = "Invalid email or password."
        return render_template("login.html", panel_name="VexPanel", error=error, is_admin=False)

    @app.route("/register", methods=["GET", "POST"], endpoint="register")
    def register_page():
        if current_user.is_authenticated: return redirect(url_for("dashboard"))
        error = None
        if request.method == "POST":
            email, password = request.form.get("email", "").strip().lower(), request.form.get("password", "")
            if len(password) < 12: error = "Use a password of at least 12 characters."
            else:
                try: db.create_user(email, password); login_user(User(db.get_user_by_email(email))); return redirect(url_for("dashboard"))
                except Exception: error = "Unable to create account. That email may already be registered."
        return render_template("register.html", panel_name="VexPanel", error=error, is_admin=False)

    @app.get("/logout")
    def logout_page(): logout_user(); return redirect(url_for("login"))

    @app.get("/dashboard")
    def dashboard():
        if not current_user.is_authenticated: return redirect(url_for("login"))
        with db.connect() as conn: vps_list = [dict(row) for row in conn.execute("SELECT * FROM vps WHERE user_id=?", (current_user.id,)).fetchall()]
        return render_template("dashboard.html", panel_name="VexPanel", is_admin=current_user.role in {"admin", "super_admin"}, vps_list=vps_list, notifications=[], aether_coins=0)

    @app.get("/profile")
    def profile():
        if not current_user.is_authenticated: return redirect(url_for("login"))
        return render_template("profile.html", panel_name="VexPanel", is_admin=current_user.role in {"admin", "super_admin"})

    @app.route("/create_vps", methods=["GET", "POST"])
    def create_vps_page():
        if not current_user.is_authenticated: return redirect(url_for("login"))
        if request.method == "POST":
            from .providers import get_provider
            import uuid
            hostname = request.form.get("hostname", "").strip()
            os_name = request.form.get("operating_system", "ubuntu:24.04")
            if not hostname or not all(char.isalnum() or char == "-" for char in hostname):
                return render_template("create_vps.html", panel_name="VexPanel", is_admin=False, error="Use a hostname containing letters, numbers, and hyphens only.")
            vps_id = str(uuid.uuid4())
            try:
                created = get_provider().create_vps({"id": vps_id, "hostname": hostname, "image": os_name})
                with db.connect() as conn:
                    conn.execute("INSERT INTO vps(id,user_id,provider_id,hostname,os,status,ipv4,plan) VALUES (?,?,?,?,?,?,?,?)", (vps_id, current_user.id, created["provider_id"], hostname, os_name, created["status"], created.get("ipv4"), request.form.get("plan", "Custom")))
                return redirect(url_for("dashboard"))
            except Exception:
                return render_template("create_vps.html", panel_name="VexPanel", is_admin=False, error="VPS provisioning failed. Check that your configured provider is available.")
        return render_template("create_vps.html", panel_name="VexPanel", is_admin=current_user.role in {"admin", "super_admin"})

    @app.get("/admin")
    def admin_page():
        if not current_user.is_authenticated or current_user.role not in {"admin", "super_admin"}: return redirect(url_for("dashboard"))
        with db.connect() as conn:
            users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
            vps_list = conn.execute("SELECT * FROM vps ORDER BY created_at DESC").fetchall()
        return render_template("admin.html", panel_name="VexPanel", is_admin=True, users=users, vps_list=vps_list)

    @app.get("/health")
    def health():
        return jsonify(success=True, data={"service": "vexpanel", "status": "ok"})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(success=False, error={"code": "NOT_FOUND", "message": "Resource not found."}), 404

    return app
