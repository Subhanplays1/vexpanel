# VexPanel

VexPanel is a modular Flask backend for managing provider-backed VPS instances and browser RDP environments. It intentionally does not install Docker, create infrastructure, or use a mock provider unless explicitly configured.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app wsgi run --debug
```

Set `VPS_PROVIDER=mock` only for development. `custom_docker` wraps the supplied Docker-backed provisioning model; replace its implementation with the supplied provider-specific lifecycle code when deploying to real VPS hosts.

## Boundaries retained from the supplied implementation

`app/providers/custom_docker.py` is the sole provider adapter. It does **not** install Docker or execute commands at application startup. Browser RDP is provisioned on the selected VPS through a background job; the panel host never binds the RDP port. Tunnel interfaces for TryCloudflare and Pinggy are deliberately present but disabled until a remote-command provider adapter and credential handling are configured—returning a fabricated browser URL would be unsafe.

The initial admin is only created when both bootstrap environment variables are set. Change the example password first.

## One-command installer (Linux)

```bash
chmod +x install.sh
./install.sh
```

The installer uses a virtual environment, shows an animated VexPanel banner, and leaves Docker/infrastructure provisioning under explicit operator control.
