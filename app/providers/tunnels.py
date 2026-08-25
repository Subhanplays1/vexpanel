from abc import ABC, abstractmethod

class TunnelProvider(ABC):
    """Tunnel lifecycle contract; implementations run on the target VPS, never panel host."""
    @abstractmethod
    def create(self, vps_provider, provider_id): ...
    @abstractmethod
    def stop(self, vps_provider, provider_id): ...
    @abstractmethod
    def restart(self, vps_provider, provider_id): ...
    @abstractmethod
    def get_status(self, vps_provider, provider_id): ...
    @abstractmethod
    def get_url(self, vps_provider, provider_id): ...
    @abstractmethod
    def destroy(self, vps_provider, provider_id): ...

class TryCloudflareProvider(TunnelProvider):
    def create(self, vps_provider, provider_id):
        # A worker must install cloudflared and parse its generated URL from logs.
        raise NotImplementedError("Configure the production remote-command adapter to run cloudflared on the VPS.")
    def stop(self, *args): raise NotImplementedError
    def restart(self, *args): raise NotImplementedError
    def get_status(self, *args): raise NotImplementedError
    def get_url(self, *args): raise NotImplementedError
    def destroy(self, *args): raise NotImplementedError

class PinggyProvider(TunnelProvider):
    def create(self, vps_provider, provider_id):
        raise NotImplementedError("Configure Pinggy credentials and remote-command adapter before enabling Pinggy.")
    def stop(self, *args): raise NotImplementedError
    def restart(self, *args): raise NotImplementedError
    def get_status(self, *args): raise NotImplementedError
    def get_url(self, *args): raise NotImplementedError
    def destroy(self, *args): raise NotImplementedError
