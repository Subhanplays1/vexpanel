"""Adapter for the supplied Docker provisioning system.

This is the only module that should contain provider-specific Docker calls. Replace
this adapter's methods with calls to the original host/provisioning system as needed.
"""
import docker
from .base import VPSProvider


class CustomDockerProvider(VPSProvider):
    def __init__(self, network="vexpanel_network"):
        try: self.client = docker.from_env()
        except docker.errors.DockerException as exc: raise RuntimeError("Docker provider unavailable; configure a real provider or Docker host.") from exc
        self.network = network

    def create_vps(self, spec):
        # Integrates the supplied local-container model without HTTP-driven installation.
        image = spec.get("image", "ubuntu:24.04")
        container = self.client.containers.run(image, detach=True, name=f"vexpanel-vps-{spec['id']}", hostname=spec["hostname"], tty=True)
        return {"provider_id": container.id, "status": container.status, "ipv4": None}
    def _container(self, provider_id): return self.client.containers.get(provider_id)
    def delete_vps(self, provider_id): self._container(provider_id).remove(force=True)
    def start_vps(self, provider_id): self._container(provider_id).start()
    def stop_vps(self, provider_id): self._container(provider_id).stop(timeout=20)
    def restart_vps(self, provider_id): self._container(provider_id).restart(timeout=20)
    def rebuild_vps(self, provider_id, os_name): raise NotImplementedError("Rebuild must be implemented by the production provisioning adapter.")
    def get_vps(self, provider_id):
        c = self._container(provider_id); c.reload()
        return {"provider_id": c.id, "status": c.status, "ipv4": c.attrs["NetworkSettings"].get("IPAddress") or None}
    def get_metrics(self, provider_id):
        s = self._container(provider_id).stats(stream=False); return {"cpu": s.get("cpu_stats", {}), "memory": s.get("memory_stats", {})}
    def execute_command(self, provider_id, command):
        result = self._container(provider_id).exec_run(command, demux=True)
        return result.exit_code, (result.output[0] or b"").decode(errors="replace")
