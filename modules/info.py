#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/info.py — banner + server info display
# ============================================

from modules.config import C, AUTHOR, GITHUB_URL, TELEGRAM_CHANNEL, COPYRIGHT
from modules.utils import clear, pause, get_local_ip
from modules.db import load_sites


def print_banner():
    clear()
    ip = get_local_ip()
    print(f"{C.MAGENTA}{C.BOLD}")
    print("╔══════════════════════════════════════════════╗")
    print("║       CODEX-M41NUL — Termux Hosting Panel     ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"{C.RESET}{C.GRAY}  Author : {AUTHOR}")
    print(f"  GitHub : {GITHUB_URL}")
    print(f"  Telegram: {TELEGRAM_CHANNEL}")
    print(f"  Local IP: {ip}")
    print(f"  {COPYRIGHT}{C.RESET}")
    print()


def server_info():
    print(f"\n{C.CYAN}--- Server Info ---{C.RESET}")
    ip = get_local_ip()
    print(f"  Local IP: {ip}")
    sites = load_sites()
    if not sites:
        print(f"  {C.YELLOW}No sites have been deployed yet.{C.RESET}")
    else:
        for name, s in sites.items():
            print(f"\n  {C.BOLD}{name}{C.RESET} ({s['type']})")
            print(f"    Local: http://{ip}:{s['port']}")
            if s.get("domain"):
                print(f"    Public: https://{s['domain']}")
            else:
                print(f"    Public: {C.GRAY}no custom domain attached yet{C.RESET}")
    pause()
