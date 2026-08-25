import uuid
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from ..providers import get_provider
from ..services.jobs import enqueue
from ..services.rdp import RDPService

vps_api = Blueprint("vps", __name__)

def response(data, status=200): return jsonify(success=True, data=data), status
def error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
def owned(vps_id):
    db = current_app.extensions["vexpanel_db"]
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM vps WHERE id=? AND user_id=?", (vps_id, int(current_user.id))).fetchone()
    return row

@vps_api.get("")
@login_required
def list_vps():
    with current_app.extensions["vexpanel_db"].connect() as conn: rows = conn.execute("SELECT * FROM vps WHERE user_id=?", (current_user.id,)).fetchall()
    return response([dict(r) for r in rows])

@vps_api.post("")
@login_required
def create_vps():
    payload = request.get_json(silent=True) or {}
    hostname = payload.get("hostname", "").strip()
    os_name = payload.get("operating_system", "ubuntu:24.04")
    if not hostname or len(hostname) > 63 or not all(c.isalnum() or c == '-' for c in hostname): return error("INVALID_HOSTNAME", "Hostname must be 1-63 letters, digits, or hyphens.", 422)
    vps_id = str(uuid.uuid4())
    try: created = get_provider().create_vps({"id": vps_id, "hostname": hostname, "image": os_name})
    except Exception: return error("VPS_CREATION_FAILED", "Provider could not create the VPS.", 502)
    with current_app.extensions["vexpanel_db"].connect() as db: db.execute("INSERT INTO vps(id,user_id,provider_id,hostname,os,status,ipv4,plan) VALUES (?,?,?,?,?,?,?,?)", (vps_id, current_user.id, created["provider_id"], hostname, os_name, created["status"], created.get("ipv4"), payload.get("plan")))
    current_app.extensions["vexpanel_db"].audit(current_user.id, "vps.create", vps_id)
    return response({"id": vps_id, "status": created["status"]}, 201)

@vps_api.get("/<vps_id>")
@login_required
def get_vps(vps_id):
    row = owned(vps_id)
    if not row: return error("NOT_FOUND", "VPS not found.", 404)
    return response(dict(row))

@vps_api.post("/<vps_id>/<action>")
@login_required
def lifecycle(vps_id, action):
    row = owned(vps_id)
    if not row or action not in {"start", "stop", "restart", "delete"}: return error("NOT_FOUND", "VPS action not found.", 404)
    provider = get_provider()
    try:
        if action == "delete":
            provider.delete_vps(row["provider_id"])
            with current_app.extensions["vexpanel_db"].connect() as db: db.execute("DELETE FROM vps WHERE id=?", (vps_id,))
        else: getattr(provider, f"{action}_vps")(row["provider_id"])
    except Exception: return error("PROVIDER_ACTION_FAILED", "Provider action failed.", 502)
    current_app.extensions["vexpanel_db"].audit(current_user.id, f"vps.{action}", vps_id)
    return response({"id": vps_id, "action": action})

@vps_api.get("/<vps_id>/rdp")
@login_required
def get_rdp(vps_id):
    if not owned(vps_id): return error("NOT_FOUND", "VPS not found.", 404)
    with current_app.extensions["vexpanel_db"].connect() as db: row = db.execute("SELECT * FROM rdp_instances WHERE vps_id=?", (vps_id,)).fetchone()
    return response(dict(row) if row else None)

@vps_api.post("/<vps_id>/rdp")
@login_required
def create_rdp(vps_id):
    row = owned(vps_id)
    if not row: return error("NOT_FOUND", "VPS not found.", 404)
    user_id = int(current_user.id)  # Capture before the request context ends.
    job_id = enqueue("RDP_INSTALL", vps_id, lambda: RDPService().install(row, user_id))
    current_app.extensions["vexpanel_db"].audit(user_id, "rdp.create", vps_id)
    return response({"job_id": job_id, "status": "QUEUED"}, 202)

@vps_api.get("/<vps_id>/rdp/status")
@login_required
def rdp_status(vps_id): return get_rdp(vps_id)
