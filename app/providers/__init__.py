from flask import current_app
from .custom_docker import CustomDockerProvider
from .mock import MockProvider

def get_provider():
    provider = current_app.extensions.get("vps_provider")
    if provider: return provider
    if current_app.config["VPS_PROVIDER"] == "mock": provider = MockProvider()
    else: provider = CustomDockerProvider(current_app.config["DOCKER_NETWORK"])
    current_app.extensions["vps_provider"] = provider
    return provider
