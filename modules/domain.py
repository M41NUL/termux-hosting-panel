#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/domain.py — custom domain attach + instructions
# ============================================

from modules.config import C
from modules.utils import pause
from modules.db import load_sites, save_sites
from modules.sites import choose_site


def domain_setup():
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites found. Deploy a site first.{C.RESET}")
        return pause()

    print(f"\n{C.CYAN}--- Domain Setup ---{C.RESET}")
    name = choose_site(sites)
    if not name:
        return pause()

    domain = input("Enter domain name (e.g. mysite.com): ").strip().lower()
    if not domain or "." not in domain:
        print(f"{C.RED}Invalid domain.{C.RESET}")
        return pause()

    for other, s in sites.items():
        if s.get("domain") == domain and other != name:
            print(f"{C.RED}This domain is already attached to '{other}'.{C.RESET}")
            return pause()

    sites[name]["domain"] = domain
    save_sites(sites)

    print(f"\n{C.GREEN}✔ Domain '{domain}' attached to '{name}'{C.RESET}")
    print(f"\n{C.YELLOW}Follow these steps to make the domain live:{C.RESET}")
    print(f"  1. cloudflared tunnel route dns tcp-panel {domain}")
    print("  2. Add this ingress rule to ~/.cloudflared/config.yml:")
    print(f"       - hostname: {domain}")
    print(f"         service: http://localhost:{sites[name]['port']}")
    print("  3. pm2 restart tcp_tunnel  (to restart the tunnel)")
    print("  4. Wait 1-5 minutes for DNS to propagate")
    pause()
