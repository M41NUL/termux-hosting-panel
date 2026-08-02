#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/db.py — JSON-file storage helpers
# ============================================

import json

from modules.config import SITES_DB, PORT_START, PORT_END


def load_sites():
    try:
        with open(SITES_DB) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_sites(data):
    with open(SITES_DB, "w") as f:
        json.dump(data, f, indent=2)


def allocate_port():
    sites = load_sites()
    used = {s["port"] for s in sites.values() if "port" in s}
    for p in range(PORT_START, PORT_END + 1):
        if p not in used:
            return p
    raise Exception("Kono free port pawa jayni.")
