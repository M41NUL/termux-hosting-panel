#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/utils.py — shared helper functions
# ============================================

import os
import shutil
import socket
import subprocess

from modules.config import C


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def pause():
    input(f"\n{C.GRAY}Press Enter to continue...{C.RESET}")


def run(cmd, capture=False):
    """Run a shell command. Returns (returncode, stdout, stderr)."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)


def command_exists(cmd):
    return shutil.which(cmd) is not None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def pm2_name(site_name):
    return f"tcp_{site_name}"
