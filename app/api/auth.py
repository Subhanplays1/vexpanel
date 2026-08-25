from flask import Blueprint, current_app, jsonify, request
from flask_login import login_user, logout_user, login_required
from ..auth import User
from .. import limiter

auth_api = Blueprint("auth", __name__)

@auth_api.post("/login")
@limiter.limit("5 per minute")
def login():
    payload = request.get_json(silent=True) or {}
    email, password = payload.get("email", ""), payload.get("password", "")
    user = current_app.extensions["vexpanel_db"].verify_user(email, password)
    if not user: return jsonify(success=False, error={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}), 401
    login_user(User(user)); return jsonify(success=True, data={"email": user["email"], "role": user["role"]})

@auth_api.post("/logout")
@login_required
def logout(): logout_user(); return jsonify(success=True, data={})
