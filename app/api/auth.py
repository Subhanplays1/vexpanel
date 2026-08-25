import re
import sqlite3
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_user, logout_user, login_required
from ..auth import User
from .. import limiter

auth_api = Blueprint("auth", __name__)

@auth_api.post("/register")
@limiter.limit("3 per minute")
def register():
    payload = request.get_json(silent=True) or {}
    email, password = payload.get("email", "").strip().lower(), payload.get("password", "")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify(success=False, error={"code":"INVALID_EMAIL","message":"Enter a valid email address."}), 422
    if len(password) < 12:
        return jsonify(success=False, error={"code":"WEAK_PASSWORD","message":"Use a password of at least 12 characters."}), 422
    db = current_app.extensions["vexpanel_db"]
    try: db.create_user(email, password)
    except sqlite3.IntegrityError:
        return jsonify(success=False, error={"code":"EMAIL_EXISTS","message":"An account with this email already exists."}), 409
    user = db.get_user_by_email(email)
    login_user(User(user))
    return jsonify(success=True, data={"email": user["email"], "role": user["role"]}), 201

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
