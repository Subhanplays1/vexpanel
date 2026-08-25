import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


class Database:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS vps (id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, provider_id TEXT NOT NULL, hostname TEXT NOT NULL, os TEXT NOT NULL, status TEXT NOT NULL, ipv4 TEXT, plan TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));
            CREATE TABLE IF NOT EXISTS rdp_instances (id TEXT PRIMARY KEY, vps_id TEXT UNIQUE NOT NULL, user_id INTEGER NOT NULL, status TEXT NOT NULL, docker_container_id TEXT, docker_container_name TEXT, docker_image TEXT NOT NULL DEFAULT 'akarita/docker-ubuntu-desktop', internal_host TEXT NOT NULL DEFAULT 'localhost', internal_port INTEGER NOT NULL DEFAULT 6080, tunnel_provider TEXT, tunnel_status TEXT, tunnel_url TEXT, last_error TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, type TEXT NOT NULL, status TEXT NOT NULL, vps_id TEXT, logs TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT NOT NULL, resource TEXT NOT NULL, result TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            ''')

    def bootstrap_admin(self, email, password):
        if email and password and not self.get_user_by_email(email): self.create_user(email, password, "super_admin")
    def create_user(self, email, password, role="user"):
        with self.connect() as db: db.execute("INSERT INTO users(email,password_hash,role) VALUES (?,?,?)", (email.lower(), generate_password_hash(password), role))
    def get_user(self, user_id):
        with self.connect() as db: return db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    def get_user_by_email(self, email):
        with self.connect() as db: return db.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()
    def verify_user(self, email, password):
        user = self.get_user_by_email(email)
        return user if user and check_password_hash(user["password_hash"], password) else None
    def audit(self, user_id, action, resource, result="success"):
        with self.connect() as db: db.execute("INSERT INTO audit_logs(user_id,action,resource,result) VALUES (?,?,?,?)", (user_id, action, resource, result))
