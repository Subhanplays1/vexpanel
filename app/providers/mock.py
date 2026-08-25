import uuid
from .base import VPSProvider

class MockProvider(VPSProvider):
    def __init__(self): self.items = {}
    def create_vps(self, spec):
        pid = str(uuid.uuid4()); self.items[pid] = {"provider_id": pid, "status": "running", "ipv4": "203.0.113.10"}; return self.items[pid]
    def delete_vps(self, provider_id): self.items.pop(provider_id, None)
    def start_vps(self, provider_id): self.items[provider_id]["status"] = "running"
    def stop_vps(self, provider_id): self.items[provider_id]["status"] = "stopped"
    def restart_vps(self, provider_id): self.start_vps(provider_id)
    def rebuild_vps(self, provider_id, os_name): self.restart_vps(provider_id)
    def get_vps(self, provider_id): return self.items[provider_id]
    def get_metrics(self, provider_id): return {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0}
    def execute_command(self, provider_id, command): return 0, "mock provider: command not executed"
