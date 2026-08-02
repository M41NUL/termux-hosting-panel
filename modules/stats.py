#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/stats.py — system stats (CPU/RAM/storage/battery)
# ============================================

import json

from modules.config import C
from modules.utils import run, pause, command_exists


def system_stats():
    print(f"\n{C.CYAN}--- System Stats ---{C.RESET}")

    try:
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        total = int([l for l in meminfo.split("\n") if "MemTotal" in l][0].split()[1]) // 1024
        free = int([l for l in meminfo.split("\n") if "MemAvailable" in l][0].split()[1]) // 1024
        used = total - free
        print(f"  RAM: {used}MB / {total}MB used ({round(used/total*100)}%)")
    except Exception:
        print(f"  RAM: {C.GRAY}unavailable{C.RESET}")

    code, out, _ = run("df -h $HOME | tail -1", capture=True)
    if out:
        parts = out.split()
        if len(parts) >= 5:
            print(f"  Storage: {parts[2]} used / {parts[1]} total ({parts[4]})")

    if command_exists("termux-battery-status"):
        code, out, _ = run("termux-battery-status", capture=True)
        try:
            batt = json.loads(out)
            print(f"  Battery: {batt.get('percentage')}% ({batt.get('status')})")
        except Exception:
            print(f"  Battery: {C.GRAY}unavailable{C.RESET}")
    else:
        print(f"  Battery: {C.GRAY}install Termux:API app for this{C.RESET}")

    code, out, _ = run("pm2 jlist", capture=True)
    try:
        procs = json.loads(out or "[]")
        tcp_procs = [p for p in procs if p["name"].startswith("tcp_")]
        print(f"  Active PM2 processes: {len(tcp_procs)}")
    except Exception:
        pass

    pause()
