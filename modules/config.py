#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/config.py — paths, constants, developer info
# ============================================

import os
from datetime import datetime

# ============================================
# DEVELOPER INFORMATION
# ============================================
AUTHOR = "Md. Mainul Islam"
OWNER = "CODEX-M41NUL"
GITHUB = "M41NUL"
GITHUB_URL = "https://github.com/M41NUL"
WHATSAPP = "+8801308850528"
TELEGRAM = "t.me/mdmainulislaminfo"
TELEGRAM_CHANNEL = "https://t.me/codexm41nul"
TELEGRAM_GROUP = "https://t.me/codex_m41nul"
EMAIL = "devmainulislam@gmail.com"
YOUTUBE = "https://youtube.com/@codexm41nul"
YEAR = datetime.now().year
COPYRIGHT = f"© {YEAR} CODEX-M41NUL. All Rights Reserved."

# ============================================
# PATHS
# ============================================
HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, "tcp-panel")
SITES_DIR = os.path.join(BASE_DIR, "sites")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
SITES_DB = os.path.join(CONFIG_DIR, "sites.json")
SETUP_FLAG = os.path.join(CONFIG_DIR, ".setup_done")
CLOUDFLARED_CONFIG = os.path.join(HOME, ".cloudflared", "config.yml")

# ============================================
# PORT RANGE
# ============================================
PORT_START = 3000
PORT_END = 3999


def ensure_dirs():
    for d in [BASE_DIR, SITES_DIR, LOGS_DIR, CONFIG_DIR, BACKUPS_DIR]:
        os.makedirs(d, exist_ok=True)


# ============================================
# TERMINAL COLORS
# ============================================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
