import uuid
from flask import current_app
from dataclasses import dataclass
from ..providers import get_provider

RDP_IMAGE = "akarita/docker-ubuntu-desktop"

@dataclass
class RDPService:
    def install(self, vps, user_id):
        """Runs via worker in production; uses controlled fixed Docker commands only."""
        db = current_app.extensions["vexpanel_db"]
        rdp_id, name = str(uuid.uuid4()), f"vexpanel-rdp-{vps['id']}"
        with db.connect() as conn:
            old = conn.execute("SELECT * FROM rdp_instances WHERE vps_id=?", (vps["id"],)).fetchone()
            if old: return dict(old)
            conn.execute("INSERT INTO rdp_instances(id,vps_id,user_id,status,docker_container_name) VALUES (?,?,?,?,?)", (rdp_id, vps["id"], user_id, "SELECTING_TUNNEL", name))
        # Exact image and fixed port; no caller-supplied Docker arguments are ever accepted.
        code, output = get_provider().execute_command(vps["provider_id"], ["docker", "run", "-d", "--platform=linux/amd64", "--name", name, "--restart", "unless-stopped", "-p", "6080:6080", RDP_IMAGE])
        if code:
            with db.connect() as conn: conn.execute("UPDATE rdp_instances SET status='ERROR',last_error=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (output[-1000:], rdp_id))
        with db.connect() as conn:
            return dict(conn.execute("SELECT * FROM rdp_instances WHERE id=?", (rdp_id,)).fetchone())
