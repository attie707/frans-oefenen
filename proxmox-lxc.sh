#!/usr/bin/env bash
# Frans oefenen: Proxmox helper script.
# Run this on the Proxmox HOST (as root). It creates a small Debian LXC and installs the app inside it.
#
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/attie707/frans-oefenen/main/proxmox-lxc.sh)"
#
# Optional settings (put them in front of the command, e.g.  CTID=150 MEM=512 bash -c "$(curl ...)"):
#   CTID      container ID              (default: next free ID)
#   CT_NAME   hostname                  (default: frans-oefenen)
#   MEM       RAM in MB                 (default: 256)
#   DISK      disk in GB                (default: 2)
#   CORES     CPU cores                 (default: 1)
#   BRIDGE    network bridge            (default: vmbr0)
#   IP        "dhcp" or e.g. "192.168.1.50/24,gw=192.168.1.1"   (default: dhcp)
#   STORAGE   storage for the disk      (default: first storage that allows containers, e.g. local-lvm)
#   REPO      git repository            (default: https://github.com/attie707/frans-oefenen.git)
set -euo pipefail

REPO="${REPO:-https://github.com/attie707/frans-oefenen.git}"
CT_NAME="${CT_NAME:-frans-oefenen}"
MEM="${MEM:-256}"
DISK="${DISK:-2}"
CORES="${CORES:-1}"
BRIDGE="${BRIDGE:-vmbr0}"
IP="${IP:-dhcp}"
PORT=8000
# avoid locale warnings: the SSH session's LANG usually isn't installed in a fresh container
export LANG=C.UTF-8 LC_ALL=C.UTF-8
unset LANGUAGE

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()  { printf '\033[1;32m ✓\033[0m %s\n' "$*"; }
die() { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "Run this as root on the Proxmox host."
command -v pct >/dev/null || die "pct not found. Run this on the Proxmox host, not inside a container."

CTID="${CTID:-$(pvesh get /cluster/nextid)}"
pct status "$CTID" >/dev/null 2>&1 && die "Container ID $CTID already exists. Choose another with CTID=..."

TPL_STORAGE=$(pvesm status -content vztmpl 2>/dev/null | awk 'NR>1 && $3=="active"{print $1; exit}')
STORAGE="${STORAGE:-$(pvesm status -content rootdir 2>/dev/null | awk 'NR>1 && $3=="active"{print $1; exit}')}"
[ -n "$TPL_STORAGE" ] || die "No storage found that can hold container templates (e.g. 'local')."
[ -n "$STORAGE" ] || die "No storage found that can hold containers (e.g. 'local-lvm')."

if [ "$IP" = "dhcp" ]; then NET="name=eth0,bridge=$BRIDGE,ip=dhcp"; else NET="name=eth0,bridge=$BRIDGE,ip=$IP"; fi

echo
say "Creating LXC $CTID '$CT_NAME'  (${MEM} MB RAM, ${DISK} GB disk on $STORAGE, network: $IP)"

# ---- Debian template ----
say "Looking up the latest Debian template"
pveam update >/dev/null
TEMPLATE=$(pveam available --section system | awk '{print $2}' | grep -E '^debian-[0-9]+-standard' | sort -V | tail -1)
[ -n "$TEMPLATE" ] || die "Could not find a Debian template."
if ! pveam list "$TPL_STORAGE" | grep -q "$TEMPLATE"; then
  say "Downloading $TEMPLATE"
  pveam download "$TPL_STORAGE" "$TEMPLATE" >/dev/null
fi
ok "Template: $TEMPLATE"

# ---- create + start ----
pct create "$CTID" "$TPL_STORAGE:vztmpl/$TEMPLATE" \
  --hostname "$CT_NAME" --memory "$MEM" --swap 256 --cores "$CORES" \
  --rootfs "$STORAGE:$DISK" --net0 "$NET" \
  --unprivileged 1 --features nesting=1 --onboot 1 --timezone host \
  --description "Frans oefenen: http://<ip>:$PORT  ·  update: run 'update' in the console" >/dev/null
ok "Container created"
pct start "$CTID"
say "Waiting for network"
for i in $(seq 1 30); do
  pct exec "$CTID" -- getent hosts deb.debian.org >/dev/null 2>&1 && break
  sleep 2
  [ "$i" -eq 30 ] && die "Container has no internet connection. Check bridge ($BRIDGE) and IP settings."
done
ok "Network is up"

# ---- install inside the container ----
SETUP=$(mktemp)
cat > "$SETUP" <<EOF
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get -y -qq upgrade >/dev/null
apt-get install -y -qq python3 git ca-certificates >/dev/null
id frans >/dev/null 2>&1 || useradd --system --home /var/lib/frans-oefenen --shell /usr/sbin/nologin frans
mkdir -p /var/lib/frans-oefenen && chown frans: /var/lib/frans-oefenen
rm -rf /opt/frans-oefenen
git clone --depth 1 "$REPO" /opt/frans-oefenen

cat > /etc/systemd/system/frans-oefenen.service <<'UNIT'
[Unit]
Description=Frans oefenen
After=network-online.target
Wants=network-online.target

[Service]
User=frans
WorkingDirectory=/opt/frans-oefenen/app
Environment=DATA_DIR=/var/lib/frans-oefenen PORT=$PORT QUIET=1
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
RestartSec=3
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
UNIT

cat > /usr/local/bin/update <<'UPD'
#!/usr/bin/env bash
set -e
export LANG=C.UTF-8 LC_ALL=C.UTF-8
echo "Updating Frans oefenen..."
git -C /opt/frans-oefenen pull --ff-only
systemctl restart frans-oefenen
echo "Done. Scores and accounts are kept in /var/lib/frans-oefenen"
UPD
chmod +x /usr/local/bin/update

cat > /usr/local/bin/backup <<'BAK'
#!/usr/bin/env bash
set -e
f=/root/frans-backup-\$(date +%F).db
python3 -c "import sqlite3;s=sqlite3.connect('/var/lib/frans-oefenen/frans.db');d=sqlite3.connect('\$f');s.backup(d)"
echo "Backup written to \$f"
BAK
chmod +x /usr/local/bin/backup

systemctl daemon-reload
systemctl enable --now frans-oefenen >/dev/null 2>&1
EOF
say "Installing Python and the app (takes a minute)"
pct push "$CTID" "$SETUP" /root/setup.sh
rm -f "$SETUP"
pct exec "$CTID" -- bash /root/setup.sh
pct exec "$CTID" -- rm -f /root/setup.sh
sleep 2
pct exec "$CTID" -- systemctl is-active --quiet frans-oefenen || die "The service did not start. Check: pct exec $CTID -- journalctl -u frans-oefenen"
ok "App is running"

CT_IP=$(pct exec "$CTID" -- hostname -I | awk '{print $1}')
pct set "$CTID" --description "Frans oefenen: http://$CT_IP:$PORT  ·  update: run 'update' in the console" >/dev/null

echo
printf '\033[1;32mDone!\033[0m  Open \033[1mhttp://%s:%s\033[0m and create the admin account straight away.\n\n' "$CT_IP" "$PORT"
echo "  Update later:   pct exec $CTID -- update      (or type 'update' in the container console)"
echo "  Backup:         pct exec $CTID -- backup"
echo "  Logs:           pct exec $CTID -- journalctl -u frans-oefenen -f"
echo
