#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/filemanager.py — browse/add/delete/view site files
# ============================================

import os
import shutil

from modules.config import C
from modules.utils import pause
from modules.db import load_sites
from modules.sites import choose_site


def file_manager():
    sites = load_sites()
    if not sites:
        print(f"{C.YELLOW}No sites found.{C.RESET}")
        return pause()

    name = choose_site(sites)
    if not name:
        return pause()
    site_dir = sites[name]["dir"]

    while True:
        print(f"\n{C.CYAN}--- File Manager: {name} ---{C.RESET}")
        print("[1] List files  [2] Upload/Add file  [3] Delete file  [4] View file  [0] Back")
        choice = input("Select: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            _list_files(site_dir)
            pause()
        elif choice == "2":
            _add_file(site_dir)
            pause()
        elif choice == "3":
            _delete_file(site_dir)
            pause()
        elif choice == "4":
            _view_file(site_dir)
            pause()
        else:
            print(f"{C.RED}Invalid option.{C.RESET}")
            pause()


def _list_files(site_dir):
    for root, dirs, files in os.walk(site_dir):
        rel = os.path.relpath(root, site_dir)
        for f in files:
            shown = f if rel == "." else os.path.join(rel, f)
            print(f"  {shown}")


def _add_file(site_dir):
    src = input("Enter path of file to add: ").strip().strip('"')
    src = os.path.expanduser(src)
    if not os.path.exists(src):
        print(f"{C.RED}File not found.{C.RESET}")
        return
    dest_name = input("Save as what name in the site (blank = same name): ").strip()
    dest_name = dest_name or os.path.basename(src)
    dest_path = os.path.join(site_dir, dest_name)
    parent = os.path.dirname(dest_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copy(src, dest_path)
    print(f"{C.GREEN}✔ Added: {dest_name}{C.RESET}")


def _delete_file(site_dir):
    rel_path = input("Enter relative path of file to delete: ").strip()
    target = os.path.join(site_dir, rel_path)
    if not os.path.abspath(target).startswith(os.path.abspath(site_dir)):
        print(f"{C.RED}Invalid path.{C.RESET}")
        return
    if os.path.exists(target):
        os.remove(target) if os.path.isfile(target) else shutil.rmtree(target)
        print(f"{C.GREEN}✔ Deleted: {rel_path}{C.RESET}")
    else:
        print(f"{C.RED}File not found.{C.RESET}")


def _view_file(site_dir):
    rel_path = input("Enter relative path of file to view: ").strip()
    target = os.path.join(site_dir, rel_path)
    if os.path.exists(target) and os.path.isfile(target):
        try:
            with open(target, "r", errors="replace") as f:
                print(f"\n{C.GRAY}--- {rel_path} ---{C.RESET}")
                print(f.read()[:3000])
        except Exception as e:
            print(f"{C.RED}Error: {e}{C.RESET}")
    else:
        print(f"{C.RED}File not found.{C.RESET}")
