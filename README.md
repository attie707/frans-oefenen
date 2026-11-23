# Frans oefenen

A small French practice web app (être, avoir, -er verbs). It's pure Python with **no dependencies**
and uses SQLite for storage. It uses about 20 MB of RAM.

## Install on Proxmox (recommended)

Run this in the **Proxmox host shell**. It creates a small Debian LXC (256 MB RAM, 2 GB disk) and installs the app as a service. Docker isn't needed.

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/attie707/frans-oefenen/main/proxmox-lxc.sh)"
```

At the end it prints the address. Settings you can put in front of the command: `CTID=150 MEM=512 IP=192.168.1.50/24,gw=192.168.1.1 BRIDGE=vmbr0 STORAGE=local-lvm`.

| Task | Command (on the Proxmox host) |
|---|---|
| Update | `pct exec <ID> -- update` |
| Backup | `pct exec <ID> -- backup` |
| Logs | `pct exec <ID> -- journalctl -u frans-oefenen -f` |

## Alternative: install on an existing Docker host

Run this on the Docker host (replace `<user>` with your GitHub name):

```bash
curl -fsSL https://raw.githubusercontent.com/<user>/frans-oefenen/main/install.sh | sudo bash -s -- https://github.com/<user>/frans-oefenen.git
```

It installs git if needed, clones the code to `/opt/frans-oefenen` and starts the container.

**Update** (after you've changed something on GitHub):

```bash
sudo bash /opt/frans-oefenen/install.sh
```

Scores and accounts are kept in a Docker volume, so updates never touch them.

Open `http://<ip-of-docker-host>:8000` from any device on your network.
1. The first visit asks you to create an **admin** account (for a parent or teacher).
2. Go to **Beheer** → add a student account for your son.
3. He logs in on his phone, tablet or laptop and starts practising.

The first visitor can create the admin account, so do step 1 straight away.

## What's inside

| Part | What it does |
|---|---|
| Meerkeuze | 5 options, keys 1–5 work. The wrong options are typical mistakes (ils sont/ils ont, tu est…). Mixes "nous ___ (avoir)" with Dutch→French. Focus on être/avoir, -er verbs, everything, or **zwakke punten** (only the ones he got wrong). |
| Spelling | Typing, with 5 levels that unlock at 80% of the last 20 answers: être/avoir → -er verbs → full translations → tricky cases (mangeons, commençons, j'aime) → negation (je ne suis pas). Accent buttons for phones. A missing accent counts as "bijna" (almost). |
| Luisteren | The browser reads French aloud (🔊, 🐢 slow). **Wat hoor je?**: choose the Dutch meaning. **Dictee**: write down what you hear. Forms that sound the same (il parle / ils parlent) are both accepted, and the feedback explains why. Needs a French voice on the device (standard on phones; on Windows install French under Language settings). |
| Herhaling | Leitner system: each item sits in a box from 1 to 5. Wrong answers go back to box 1 and are asked much more often. |
| Snelheidsronde | 60 seconds with a high score. The score is counted on the server, so it can't be faked. |
| Motivation | XP, ranks (Débutant → Légende), daily goal of 20 questions, day streak, 🔊 pronunciation (browser voice). |
| Scores | 14-day chart, verb × person grid, weak points, recent mistakes, **CSV export** (opens correctly in Excel). Admins can view every student. |

## Practice away from home
Don't open a port on the router. Install **Tailscale** on the Docker host (or as a Proxmox LXC)
and on his phone, then use the Tailscale IP. If you ever want to open it to other students on the
internet, put it behind a reverse proxy with HTTPS (Nginx Proxy Manager, Caddy, Traefik) and set
`COOKIE_SECURE=1`.

## Adding verbs
Edit `ER_VERBS` in `app/content.py` (French + Dutch forms), then run `docker compose up -d --build`.
Scores are kept.

## Backup
`docker run --rm -v frans-oefenen_frans-data:/d -v $PWD:/b alpine cp /d/frans.db /b/`

## Without Docker
`cd app && python3 server.py` (Python 3.9+), then open http://localhost:8000
