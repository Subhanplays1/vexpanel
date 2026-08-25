from flask import Blueprint, current_app, jsonify
from flask_login import login_required
from ..auth import admin_required

admin_api = Blueprint("admin", __name__)

@admin_api.get("/overview")
@login_required
@admin_required
def overview():
    with current_app.extensions["vexpanel_db"].connect() as db:
        counts = {key: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for key, table in {"users":"users", "vps":"vps", "rdp_instances":"rdp_instances", "running_jobs":"jobs WHERE status='RUNNING'"}.items()}
    return jsonify(success=True, data=counts)
