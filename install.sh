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

package_manager() {
  if need_command apt-get; then printf 'apt'
  elif need_command dnf; then printf 'dnf'
  elif need_command pacman; then printf 'pacman'
  else return 1
  fi
}

install_packages() {
  local manager
  manager="$(package_manager)" || { printf '%bUnsupported package manager.%b\n' "$YELLOW" "$RESET"; exit 1; }
  case "$manager" in
    apt) sudo apt-get update && sudo apt-get install -y "$@" ;;
    dnf) sudo dnf install -y "$@" ;;
    pacman) sudo pacman -Sy --noconfirm "$@" ;;
  esac
}

install_dependencies() {
  local manager
  manager="$(package_manager)" || { printf '%bUnsupported package manager. Install Python 3.11+, pip, venv, git, curl, and Docker manually.%b\n' "$YELLOW" "$RESET"; exit 1; }

  # Finish a prior interrupted installation before asking apt/dnf/pacman to act.
  if [[ "$manager" == "apt" ]]; then
    sudo dpkg --configure -a
  fi

  printf '%bInstalling missing system dependencies…%b\n' "$YELLOW" "$RESET"
  case "$manager" in
    apt)
      need_command python3 || install_packages python3
      python3 -m venv --help >/dev/null 2>&1 || install_packages python3-venv
      python3 -m pip --version >/dev/null 2>&1 || install_packages python3-pip
      need_command curl || install_packages curl ca-certificates
      ;;
    dnf)
      need_command python3 || install_packages python3 python3-pip
      python3 -m pip --version >/dev/null 2>&1 || install_packages python3-pip
      need_command curl || install_packages curl ca-certificates
      ;;
    pacman)
      need_command python3 || install_packages python python-pip
      python3 -m pip --version >/dev/null 2>&1 || install_packages python-pip
      need_command curl || install_packages curl ca-certificates
      ;;
  esac

  # The standard Ubuntu/Debian Docker package is reliable for this local-Docker provider.
  if ! need_command docker; then
    printf '%bDocker was not found. Installing it…%b\n' "$YELLOW" "$RESET"
    case "$manager" in
      apt) install_packages docker.io ;;
      dnf) install_packages docker ;;
      pacman) install_packages docker ;;
    esac
  fi

  if need_command systemctl; then
    sudo systemctl enable --now docker 2>/dev/null || true
  fi

  # Covers systems where Python was present but no ensurepip/venv module existed.
  if ! python3 -m venv --help >/dev/null 2>&1; then
    printf '%bInstalling Python virtual-environment support…%b\n' "$YELLOW" "$RESET"
    case "$manager" in
      apt) install_packages python3-venv ;;
      dnf) install_packages python3-virtualenv ;;
      pacman) install_packages python-virtualenv ;;
    esac
  fi
}

animate_banner
printf '  This installs all required system and Python dependencies automatically.\n'
printf '  Docker is installed only when missing; VPS resources are never provisioned.\n\n'
read -r -p '  Press Enter to install, or Ctrl+C to cancel… ' _

install_dependencies
cd "$PROJECT_DIR"
rm -rf .venv
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
