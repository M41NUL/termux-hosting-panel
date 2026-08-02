#!/usr/bin/env python3
# ============================================
# CODEX-M41NUL — Termux Hosting Panel
# modules/deploy.py — site type detection & deploy logic
# ============================================

import os
import json
import shutil
import time
import zipfile
from datetime import datetime

from modules.config import SITES_DIR, BASE_DIR, C
from modules.utils import run, pause, pm2_name
from modules.db import load_sites, save_sites, allocate_port


def detect_site_type(path):
    files = os.listdir(path)
    if "package.json" in files:
        return "node"
    if any(f in files for f in ("requirements.txt", "app.py", "main.py", "wsgi.py")):
        return "python"
    if "index.html" in files or any(f.endswith(".html") for f in files):
        return "static"
    return None


def find_entry(path, site_type):
    files = os.listdir(path)
    if site_type == "node":
        pkg_path = os.path.join(path, "package.json")
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path) as f:
                    pkg = json.load(f)
                if pkg.get("main"):
                    return pkg["main"]
            except Exception:
                pass
        for cand in ("server.js", "index.js", "app.js"):
            if cand in files:
                return cand
        return None
    if site_type == "python":
        for cand in ("app.py", "main.py", "wsgi.py"):
            if cand in files:
                return cand
        return None
    return None


def write_static_server(path, port):
    server_path = os.path.join(path, "__tcp_static_server.py")
    content = f'''
import http.server
import socketserver
import os

PORT = {port}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Static site running on port {{PORT}}")
    httpd.serve_forever()
'''
    with open(server_path, "w") as f:
        f.write(content)
    return "__tcp_static_server.py"


def extract_zip(zip_path, dest):
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest)
    entries = os.listdir(dest)
    if len(entries) == 1 and os.path.isdir(os.path.join(dest, entries[0])):
        inner = os.path.join(dest, entries[0])
        tmp = dest + "__tmp"
        shutil.move(inner, tmp)
        shutil.rmtree(dest)
        shutil.move(tmp, dest)


def pm2_start_site(name, cwd, entry, interpreter, port):
    run(f"pm2 delete {pm2_name(name)}", capture=True)  # idempotent
    cmd = (
        f'PORT={port} pm2 start "{entry}" --name "{pm2_name(name)}" '
        f'--cwd "{cwd}" --interpreter {interpreter} --time'
    )
    code, out, err = run(cmd, capture=True)
    if code != 0:
        print(f"{C.RED}PM2 start failed: {err}{C.RESET}")
    run("pm2 save", capture=True)


def deploy_site():
    print(f"\n{C.CYAN}--- Deploy New Site ---{C.RESET}")
    name = input("Enter site name (letters/numbers/-/_ only): ").strip().lower()
    if not name or not all(c.isalnum() or c in "-_" for c in name):
        print(f"{C.RED}Invalid name. Try again.{C.RESET}")
        return pause()

    sites = load_sites()
    if name in sites:
        print(f"{C.RED}A site with this name already exists.{C.RESET}")
        return pause()

    src = input("Enter folder path or .zip file path: ").strip().strip('"')
    src = os.path.expanduser(src)
    if not os.path.exists(src):
        print(f"{C.RED}Path not found: {src}{C.RESET}")
        return pause()

    site_dir = os.path.join(SITES_DIR, name)
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)

    if src.endswith(".zip"):
        print(f"{C.YELLOW}Extracting zip...{C.RESET}")
        tmp_extract = os.path.join(BASE_DIR, f"_extract_{int(time.time())}")
        extract_zip(src, tmp_extract)
        shutil.copytree(tmp_extract, site_dir)
        shutil.rmtree(tmp_extract)
    elif os.path.isfile(src):
        # Single file (e.g. one .html file) — wrap it in a new site folder.
        os.makedirs(site_dir, exist_ok=True)
        fname = os.path.basename(src)
        if fname.lower().endswith(".html"):
            dest_name = "index.html"
        else:
            dest_name = fname
        shutil.copy(src, os.path.join(site_dir, dest_name))
    else:
        shutil.copytree(src, site_dir)

    site_type = detect_site_type(site_dir)
    if not site_type:
        print(f"{C.RED}Could not detect site type. Needs index.html / package.json / requirements.txt.{C.RESET}")
        shutil.rmtree(site_dir)
        return pause()

    port = allocate_port()

    if site_type == "python" and os.path.exists(os.path.join(site_dir, "requirements.txt")):
        print(f"{C.YELLOW}Installing Python dependencies...{C.RESET}")
        run(f'pip install -r "{os.path.join(site_dir, "requirements.txt")}"')

    if site_type == "node" and os.path.exists(os.path.join(site_dir, "package.json")):
        print(f"{C.YELLOW}Installing Node dependencies...{C.RESET}")
        run(f'cd "{site_dir}" && npm install --omit=dev')

    if site_type == "static":
        entry = write_static_server(site_dir, port)
        interpreter = "python3"
    else:
        entry = find_entry(site_dir, site_type)
        if not entry:
            print(f"{C.RED}Entry file not found (server.js/app.py etc).{C.RESET}")
            return pause()
        interpreter = "node" if site_type == "node" else "python3"

    pm2_start_site(name, site_dir, entry, interpreter, port)

    sites[name] = {
        "name": name,
        "type": site_type,
        "port": port,
        "dir": site_dir,
        "entry": entry,
        "interpreter": interpreter,
        "domain": None,
        "created": datetime.now().isoformat(),
    }
    save_sites(sites)

    print(f"\n{C.GREEN}✔ Deployed '{name}' ({site_type}) on port {port}{C.RESET}")
    print(f"  Local test: http://127.0.0.1:{port}")
    pause()


def remove_site_completely(name, sites):
    run(f"pm2 delete {pm2_name(name)}", capture=True)
    run("pm2 save", capture=True)
    site_dir = sites[name]["dir"]
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    del sites[name]
    save_sites(sites)
