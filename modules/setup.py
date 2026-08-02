#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/setup.py — first-run auto dependency installer
# ============================================

import os
from datetime import datetime

from modules.config import HOME, SETUP_FLAG, C, ensure_dirs
from modules.utils import clear, pause, run, command_exists


def first_run_setup():
    ensure_dirs()
    if os.path.exists(SETUP_FLAG):
        return  # already done before

    clear()
    print(f"{C.CYAN}{C.BOLD}")
    print("============================================")
    print(" First run detected — starting auto-setup")
    print("============================================")
    print(f"{C.RESET}")

    pkgs_needed = []
    checks = {
        "node": "nodejs-lts",
        "npm": "nodejs-lts",
        "pm2": None,       # installed via npm
        "unzip": "unzip",
        "curl": "curl",
        "cloudflared": None,  # installed manually below
    }

    print("Dependency check:")
    for cmd_name, pkg in checks.items():
        found = command_exists(cmd_name)
        status = f"{C.GREEN}✔ found{C.RESET}" if found else f"{C.RED}✘ missing{C.RESET}"
        print(f"  {cmd_name:12} {status}")
        if not found and pkg and pkg not in pkgs_needed:
            pkgs_needed.append(pkg)

    if pkgs_needed:
        print(f"\n{C.YELLOW}Installing missing packages: {', '.join(pkgs_needed)}{C.RESET}")
        run("pkg update -y")
        run(f"pkg install -y {' '.join(pkgs_needed)}")

    if not command_exists("pm2"):
        print(f"\n{C.YELLOW}Installing PM2 (process manager)...{C.RESET}")
        run("npm install -g pm2")

    if not command_exists("cloudflared"):
        print(f"\n{C.YELLOW}Installing cloudflared (Cloudflare Tunnel)...{C.RESET}")
        _, arch_out, _ = run("uname -m", capture=True)
        arch = arch_out.strip()
        if arch == "aarch64":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif arch == "armv7l":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        else:
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

        local_bin = os.path.join(HOME, ".local", "bin")
        os.makedirs(local_bin, exist_ok=True)
        cf_path = os.path.join(local_bin, "cloudflared")
        run(f'curl -L "{url}" -o "{cf_path}"')
        run(f'chmod +x "{cf_path}"')

        bashrc = os.path.join(HOME, ".bashrc")
        export_line = f"export PATH=$PATH:{local_bin}"
        already = False
        if os.path.exists(bashrc):
            with open(bashrc) as f:
                already = local_bin in f.read()
        if not already:
            with open(bashrc, "a") as f:
                f.write(f"\n{export_line}\n")
        os.environ["PATH"] = os.environ.get("PATH", "") + f":{local_bin}"

    if command_exists("termux-wake-lock"):
        run("termux-wake-lock", capture=True)

    with open(SETUP_FLAG, "w") as f:
        f.write(datetime.now().isoformat())

    print(f"\n{C.GREEN}{C.BOLD}✔ Setup complete!{C.RESET}")
    pause()
