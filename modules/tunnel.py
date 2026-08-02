#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/tunnel.py — Cloudflare Tunnel controls
# ============================================

from modules.config import C
from modules.utils import run, pause


def tunnel_setup():
    print(f"\n{C.CYAN}--- Cloudflare Tunnel ---{C.RESET}")
    print("[1] Login to Cloudflare  [2] Create tunnel  [3] Start tunnel  [4] Tunnel status  [0] Back")
    choice = input("Select: ").strip()

    if choice == "1":
        run("cloudflared tunnel login")
    elif choice == "2":
        tunnel_name = input("Enter tunnel name (e.g. tcp-panel): ").strip() or "tcp-panel"
        run(f"cloudflared tunnel create {tunnel_name}")
        print(f"\n{C.YELLOW}Now create the ~/.cloudflared/config.yml file manually — see the docs.{C.RESET}")
    elif choice == "3":
        tunnel_name = input("Enter tunnel name: ").strip() or "tcp-panel"
        run("pm2 delete tcp_tunnel", capture=True)
        run(f"pm2 start cloudflared --name tcp_tunnel -- tunnel run {tunnel_name}", capture=True)
        run("pm2 save", capture=True)
        print(f"{C.GREEN}✔ Tunnel started via PM2 (tcp_tunnel){C.RESET}")
    elif choice == "4":
        run("pm2 logs tcp_tunnel --lines 30 --nostream")
    elif choice == "0":
        return
    else:
        print(f"{C.RED}Invalid option.{C.RESET}")
    pause()
