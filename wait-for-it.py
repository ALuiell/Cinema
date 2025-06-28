#!/usr/bin/env python3
import socket
import sys
import time
import subprocess

def wait_for(host, port, timeout=60, interval=2):
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, int(port)), timeout=interval):
                print(f"✅ {host}:{port} is up")
                return
        except Exception:
            elapsed = int(time.time() - start)
            if elapsed >= timeout:
                print(f"❌ Timeout waiting for {host}:{port} ({elapsed}s)")
                sys.exit(1)
            print(f"…retrying {host}:{port} ({elapsed}s elapsed)")
            time.sleep(interval)

if __name__ == "__main__":
    parts = sys.argv[1:]
    if "--" not in parts or len(parts) < 3:
        print(f"Usage: {sys.argv[0]} host:port [host:port …] -- cmd args…")
        sys.exit(1)

    idx = parts.index("--")
    services = parts[:idx]
    cmd = parts[idx+1:]

    for svc in services:
        h, p = svc.split(":")
        print(f"⏳ Waiting for {h}:{p}…")
        wait_for(h, p)

    print("🎉 All services ready, running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
