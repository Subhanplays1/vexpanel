#!/usr/bin/env bash
# VexPanel interactive installer for Debian/Ubuntu, Fedora/RHEL, and Arch Linux.
set -Eeuo pipefail

readonly PROJECT_NAME="VexPanel"
readonly PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly CYAN='\033[1;36m' PURPLE='\033[1;35m' GREEN='\033[1;32m' YELLOW='\033[1;33m' RESET='\033[0m'

cleanup() { printf '\n%bInstallation cancelled.%b\n' "$YELLOW" "$RESET"; }
trap cleanup INT TERM

frame() {
  clear
  printf "%b\n" "$PURPLE"
  printf '  ██╗   ██╗███████╗██╗  ██╗██████╗  █████╗ ███╗   ██╗███████╗██╗     \n'
  printf '  ██║   ██║██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     \n'
  printf '  ██║   ██║█████╗   ╚███╔╝ ██████╔╝███████║██╔██╗ ██║█████╗  ██║     \n'
  printf '  ╚██╗ ██╔╝██╔══╝   ██╔██╗ ██╔═══╝ ██╔══██║██║╚██╗██║██╔══╝  ██║     \n'
  printf '   ╚████╔╝ ███████╗██╔╝ ██╗██║     ██║  ██║██║ ╚████║███████╗███████╗\n'
  printf '    ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝\n%b' "$RESET"
  printf '\n%b  VPS & Browser RDP Hosting Panel%b\n' "$CYAN" "$RESET"
}

animate_banner() {
  for dots in '.' '..' '...' '....'; do
    frame
    printf '\n  %bPreparing VexPanel%s%b\n' "$GREEN" "$dots" "$RESET"
    sleep 0.16
  done
  frame
  printf '\n  %b✓ Installer ready%b\n\n' "$GREEN" "$RESET"
}

need_command() { command -v "$1" >/dev/null 2>&1; }

install_python() {
  if need_command python3; then return; fi
  printf '%bPython 3 was not found. Installing it…%b\n' "$YELLOW" "$RESET"
  if need_command apt-get; then sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
  elif need_command dnf; then sudo dnf install -y python3 python3-pip
  elif need_command pacman; then sudo pacman -Sy --noconfirm python python-pip
  else printf '%bUnsupported package manager. Install Python 3.11+ and rerun this script.%b\n' "$YELLOW" "$RESET"; exit 1
  fi
}

animate_banner
printf '  This installs Python dependencies in an isolated virtual environment.\n'
printf '  It does not install Docker or provision any VPS resources.\n\n'
read -r -p '  Press Enter to install, or Ctrl+C to cancel… ' _

install_python
cd "$PROJECT_DIR"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  printf '\n%b  Created .env. Set a long SECRET_KEY and bootstrap credentials before starting VexPanel.%b\n' "$YELLOW" "$RESET"
fi

printf '\n%b  ✓ VexPanel installed successfully%b\n' "$GREEN" "$RESET"
printf '  Start it: %bsource .venv/bin/activate && flask --app wsgi run --host 0.0.0.0%b\n' "$CYAN" "$RESET"
printf '\n  %bMade by SubhanPlays ♥%b\n\n' "$PURPLE" "$RESET"
