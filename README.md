# Zenith Testnet Faucet

Batch generate wallets and claim ZTH tokens from the Zenith EVM Testnet faucet with proxy rotation.

## Setup

```bash
pip install eth-account requests
cp proxies.txt.example proxies.txt
```

Edit `proxies.txt` with your proxy (format: `host:port:username:password`). One line = one rotating proxy. If empty, runs direct.

## Usage

```bash
python zenith.py 10              # generate 10 wallets + claim faucet
python zenith.py 20 --no-claim   # generate only, skip claims
```

## Output

Wallets are saved to `wallets.json` with addresses and private keys. Never commit this file.

## Faucet Details

- 100 ZTH per claim
- 30 minute cooldown per IP
- Proxy rotates IP per request
