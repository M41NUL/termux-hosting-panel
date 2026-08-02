#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/backup.py — backup/restore a site as zip
# ============================================

import os
import time
import zipfile

from modules.config import C, BACKUPS_DIR, SITES_DIR
from modules.utils import pause
from modules.db import load_sites
from modules.sites import choose_site


def backup_restore():
    sites = load_sites()
    print(f"\n{C.CYAN}--- Backup / Restore ---{C.RESET}")
    print("[1] Backup a site  [2] Restore a site  [0] Back")
    choice = input("Select: ").strip()

    if choice == "1":
        _backup(sites)
    elif choice == "2":
        _restore()
    elif choice == "0":
        return
    else:
        print(f"{C.RED}Invalid option.{C.RESET}")
        pause()


def _backup(sites):
    if not sites:
        print(f"{C.YELLOW}No sites found.{C.RESET}")
        return pause()
    name = choose_site(sites)
    if not name:
        return pause()
    backup_name = f"{name}_{int(time.time())}.zip"
    backup_path = os.path.join(BACKUPS_DIR, backup_name)
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(sites[name]["dir"]):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, sites[name]["dir"])
                z.write(full, rel)
    print(f"{C.GREEN}✔ Backup saved: {backup_path}{C.RESET}")
    pause()


def _restore():
    backups = os.listdir(BACKUPS_DIR) if os.path.exists(BACKUPS_DIR) else []
    if not backups:
        print(f"{C.YELLOW}No backups found.{C.RESET}")
        return pause()
    for i, b in enumerate(backups, 1):
        print(f"  [{i}] {b}")
    sel = input("Select backup number: ").strip()
    if not sel.isdigit() or not (1 <= int(sel) <= len(backups)):
        print(f"{C.RED}Invalid selection.{C.RESET}")
        return pause()
    chosen = backups[int(sel) - 1]
    print(f"{C.YELLOW}This backup will be restored under a new site name.{C.RESET}")
    new_name = input("Enter new site name: ").strip().lower()
    if not new_name:
        return pause()
    dest_dir = os.path.join(SITES_DIR, new_name)
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(BACKUPS_DIR, chosen), "r") as z:
        z.extractall(dest_dir)
    print(f"{C.GREEN}✔ Extracted to {dest_dir}. Now deploy this folder from 'Deploy New Site'.{C.RESET}")
    pause()
