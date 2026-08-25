import threading
import uuid
from flask import current_app

def enqueue(job_type, vps_id, fn):
    db = current_app.extensions["vexpanel_db"]
    job_id = str(uuid.uuid4())
    with db.connect() as conn: conn.execute("INSERT INTO jobs(id,type,status,vps_id) VALUES (?,?,?,?)", (job_id, job_type, "QUEUED", vps_id))
    app = current_app._get_current_object()
    def work():
        with app.app_context():
            with db.connect() as conn: conn.execute("UPDATE jobs SET status='RUNNING',updated_at=CURRENT_TIMESTAMP WHERE id=?", (job_id,))
            try:
                fn()
                with db.connect() as conn: conn.execute("UPDATE jobs SET status='COMPLETED',updated_at=CURRENT_TIMESTAMP WHERE id=?", (job_id,))
            except Exception as exc:
                with db.connect() as conn: conn.execute("UPDATE jobs SET status='FAILED',logs=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (str(exc)[-1500:], job_id))
    threading.Thread(target=work, daemon=True, name=f"vexpanel-{job_type}").start()
    return job_id
