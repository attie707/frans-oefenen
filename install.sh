#!/usr/bin/env bash
# Frans oefenen: install or update in one go.
#   First time:  curl -fsSL https://raw.githubusercontent.com/<user>/frans-oefenen/main/install.sh | sudo bash -s -- https://github.com/<user>/frans-oefenen.git
#   Update:      sudo bash /opt/frans-oefenen/install.sh
# Optional: DIR=/some/path to install elsewhere (default /opt/frans-oefenen)
set -euo pipefail

DIR="${DIR:-/opt/frans-oefenen}"
REPO="${1:-}"

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
die() { printf '\033[1;31mFout:\033[0m %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null || die "Docker is not installed on this machine."
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2) is missing. Install the docker-compose-plugin package."

if ! command -v git >/dev/null; then
  say "Installing git"
  if command -v apt-get >/dev/null; then apt-get update -qq && apt-get install -y -qq git
  elif command -v apk >/dev/null; then apk add --no-cache git
  elif command -v dnf >/dev/null; then dnf install -y -q git
  else die "Please install git first."; fi
fi

if [ -d "$DIR/.git" ]; then
  say "Updating $DIR"
  git -C "$DIR" pull --ff-only
else
  [ -n "$REPO" ] || die "Pass the GitHub URL the first time, e.g.: bash install.sh https://github.com/<user>/frans-oefenen.git"
  say "Downloading $REPO to $DIR"
  git clone --depth 1 "$REPO" "$DIR"
fi

cd "$DIR"
say "Building and starting the container"
docker compose up -d --build
docker image prune -f >/dev/null 2>&1 || true

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
say "Done! Open http://${IP:-<server-ip>}:8000"
say "Updating later: sudo bash $DIR/install.sh   (scores and accounts are kept)"
