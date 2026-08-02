#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# panel.py — main entry point (run this file)
# Usage: python3 panel.py
# ============================================

import sys

from modules.config import C, OWNER, ensure_dirs
from modules.utils import pause
from modules.setup import first_run_setup
from modules.info import print_banner, server_info
from modules.deploy import deploy_site
from modules.sites import list_sites, control_site, view_logs, remove_site
from modules.domain import domain_setup
from modules.filemanager import file_manager
from modules.tunnel import tunnel_setup
from modules.stats import system_stats
from modules.backup import backup_restore


def print_menu():
    from modules.db import load_sites
    sites = load_sites()
    print(f"{C.CYAN}{C.BOLD} MAIN MENU {C.RESET}")
    print(f"{C.GRAY}--------------------------------------------{C.RESET}")
    print(f"  {C.GREEN}[1]{C.RESET}  Deploy New Site")
    print(f"  {C.GREEN}[2]{C.RESET}  List All Sites  ({len(sites)} deployed)")
    print(f"  {C.GREEN}[3]{C.RESET}  Start / Stop / Restart a Site")
    print(f"  {C.GREEN}[4]{C.RESET}  View Site Logs")
    print(f"  {C.GREEN}[5]{C.RESET}  Remove a Site")
    print(f"  {C.GREEN}[6]{C.RESET}  Domain Setup (attach custom domain)")
    print(f"  {C.GREEN}[7]{C.RESET}  File Manager")
    print(f"  {C.GREEN}[8]{C.RESET}  Cloudflare Tunnel Setup / Status")
    print(f"  {C.GREEN}[9]{C.RESET}  System Stats (CPU / RAM / Storage / Battery)")
    print(f"  {C.GREEN}[10]{C.RESET} Backup / Restore a Site")
    print(f"  {C.GREEN}[11]{C.RESET} View Server Info (public URLs)")
    print(f"  {C.RED}[0]{C.RESET}  Exit")
    print(f"{C.GRAY}--------------------------------------------{C.RESET}")


def main():
    ensure_dirs()
    first_run_setup()

    actions = {
        "1": deploy_site,
        "2": list_sites,
        "3": control_site,
        "4": view_logs,
        "5": remove_site,
        "6": domain_setup,
        "7": file_manager,
        "8": tunnel_setup,
        "9": system_stats,
        "10": backup_restore,
        "11": server_info,
    }

    while True:
        print_banner()
        print_menu()
        choice = input(f"\n{C.BOLD}Select option: {C.RESET}").strip()

        if choice == "0":
            print(f"\n{C.MAGENTA}Bye! — {OWNER}{C.RESET}\n")
            sys.exit(0)
        elif choice in actions:
            actions[choice]()
        else:
            print(f"{C.RED}Invalid option.{C.RESET}")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}Exited by user.{C.RESET}")
        sys.exit(0)
