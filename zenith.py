#!/usr/bin/env python3
"""Zenith Testnet Faucet - generate wallets & claim ZTH with proxy rotation"""

import json
import time
import sys
import requests
from eth_account import Account

FAUCET_URL = "https://explorer.testnet.zenith.network/api/faucet"
WALLETS_FILE = "wallets.json"
PROXY_FILE = "proxies.txt"
CLAIM_DELAY = 2

def create_wallet():
    acct = Account.create()
    return {"address": acct.address, "private_key": acct.key.hex()}

def load_proxy():
    try:
        with open(PROXY_FILE) as f:
            line = f.readline().strip()
        if not line or line.startswith("#"):
            return None
        parts = line.split(":")
        if len(parts) == 4:
            host, port, user, pwd = parts
            return {"http": f"http://{user}:{pwd}@{host}:{port}", "https": f"http://{user}:{pwd}@{host}:{port}"}
    except FileNotFoundError:
        pass
    return None

def claim_faucet(address, proxy):
    kwargs = {"timeout": 30}
    if proxy:
        kwargs["proxies"] = proxy
    try:
        r = requests.post(FAUCET_URL, json={"address": address}, **kwargs)
        data = r.json()
        if data.get("ok"):
            return True, data.get("zthTxHash", ""), data.get("zthAmount", "0")
        return False, data.get("error", "unknown"), "0"
    except Exception as e:
        return False, str(e), "0"

def load_wallets():
    try:
        with open(WALLETS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_wallets(wallets):
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=2)

def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    claim = "--no-claim" not in sys.argv

    proxy = load_proxy()
    wallets = load_wallets()
    start_idx = len(wallets)

    print(f"[*] Generating {count} wallets...")
    for i in range(count):
        w = create_wallet()
        wallets.append(w)
        print(f"  [{start_idx + i + 1}] {w['address']}")

    save_wallets(wallets)
    print(f"[*] Saved {len(wallets)} wallets to {WALLETS_FILE}")

    if claim:
        via = "proxy" if proxy else "direct"
        print(f"\n[*] Claiming faucet ({via}, {CLAIM_DELAY}s delay)...")
        success = 0
        fail = 0
        for i in range(start_idx, len(wallets)):
            addr = wallets[i]["address"]
            ok, tx, amount = claim_faucet(addr, proxy)
            if ok:
                success += 1
                print(f"  [+] {addr[:10]}...{addr[-6:]} → {amount} ZTH")
            else:
                fail += 1
                print(f"  [-] {addr[:10]}...{addr[-6:]} → {tx}")
            if i < len(wallets) - 1:
                time.sleep(CLAIM_DELAY)

        print(f"\n[*] Done: {success} success, {fail} failed")
    else:
        print("[*] Skipping faucet claims (--no-claim)")

if __name__ == "__main__":
    main()
