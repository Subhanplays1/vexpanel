from functools import wraps
from flask import current_app, jsonify
from flask_login import UserMixin, current_user


class User(UserMixin):
    def __init__(self, data): self.id, self.email, self.role = str(data["id"]), data["email"], data["role"]


def load_user(user_id):
    row = current_app.extensions["vexpanel_db"].get_user(int(user_id))
    return User(row) if row else None


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in {"super_admin", "admin"}:
            return jsonify(success=False, error={"code": "FORBIDDEN", "message": "Administrator access required."}), 403
        return fn(*args, **kwargs)
    return wrapped
