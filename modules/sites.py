#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/sites.py — list, start/stop/restart, logs, remove
# ============================================

import json

from modules.config import C
from modules.utils import run, pause, pm2_name
from modules.db import load_sites, save_sites
from modules.deploy import pm2_start_site, remove_site_completely


def choose_site(sites):
    names = list(sites.keys())
    for i, n in enumerate(names, 1):
        print(f"  [{i}] {n}")
    sel = input("Select site number: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(names)):
        print(f"{C.RED}Invalid selection.{C.RESET}")
        return None
    return names[int(sel) - 1]


def list_sites():
    print(f"\n{C.CYAN}--- All Sites ---{C.RESET}")
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites have been deployed yet.{C.RESET}")
        return pause()

    code, out, _ = run("pm2 jlist", capture=True)
    live = {}
    try:
        for p in json.loads(out or "[]"):
            live[p["name"]] = p["pm2_env"]["status"]
    except Exception:
        pass

    print(f"{'NAME':16}{'TYPE':10}{'PORT':8}{'STATUS':12}{'DOMAIN'}")
    print("-" * 60)
    for name, s in sites.items():
        status = live.get(pm2_name(name), "stopped")
        color = C.GREEN if status == "online" else C.RED
        print(f"{name:16}{s['type']:10}{str(s['port']):8}{color}{status:12}{C.RESET}{s.get('domain') or '-'}")
    pause()


def control_site():
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites found.{C.RESET}")
        return pause()

    name = choose_site(sites)
    if not name:
        return pause()

    print("\n[1] Start  [2] Stop  [3] Restart")
    choice = input("Select: ").strip()
    action_map = {"1": "start", "2": "stop", "3": "restart"}
    action = action_map.get(choice)
    if not action:
        print(f"{C.RED}Invalid choice.{C.RESET}")
        return pause()

    if action == "start":
        s = sites[name]
        pm2_start_site(name, s["dir"], s["entry"], s["interpreter"], s["port"])
    else:
        run(f"pm2 {action} {pm2_name(name)}", capture=True)
        run("pm2 save", capture=True)

    print(f"{C.GREEN}✔ {action.capitalize()}ed '{name}'{C.RESET}")
    pause()


def view_logs():
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites found.{C.RESET}")
        return pause()
    name = choose_site(sites)
    if not name:
        return pause()
    print(f"\n{C.CYAN}--- Last 50 lines: {name} ---{C.RESET}")
    run(f"pm2 logs {pm2_name(name)} --lines 50 --nostream")
    pause()


def remove_site():
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites found.{C.RESET}")
        return pause()
    name = choose_site(sites)
    if not name:
        return pause()
    confirm = input(f"{C.RED}Confirm removal of '{name}'? (yes/no): {C.RESET}").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return pause()

    remove_site_completely(name, sites)
    print(f"{C.GREEN}✔ Removed '{name}'{C.RESET}")
    pause()
