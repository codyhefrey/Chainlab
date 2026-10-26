"""Chainlab local hash-chain demo — no cryptocurrency, nodes or distributed consensus."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path


class ChainError(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def build_chain(records):
    if not isinstance(records, list) or not 0 < len(records) <= 1000:
        raise ChainError("Provide 1 to 1000 records")
    chain = []
    previous = "0" * 64
    for index, record in enumerate(records):
        if not isinstance(record, dict) or len(json.dumps(record)) > 10_000:
            raise ChainError("Records must be JSON objects of at most 10KB")
        payload = {"index": index, "previous_hash": previous, "record": record}
        block = dict(payload, hash=digest(payload))
        chain.append(block)
        previous = block["hash"]
    return chain


def verify_chain(chain):
    if not isinstance(chain, list) or not 0 < len(chain) <= 1000:
        return False
    previous = "0" * 64
    for index, block in enumerate(chain):
        if not isinstance(block, dict) or set(block) != {"index", "previous_hash", "record", "hash"}:
            return False
        if block["index"] != index or block["previous_hash"] != previous:
            return False
        if not isinstance(block["record"], dict):
            return False
        payload = {k: block[k] for k in ("index", "previous_hash", "record")}
        if block["hash"] != digest(payload):
            return False
        previous = block["hash"]
    return True


def main():
    parser = argparse.ArgumentParser(description="Local, non-distributed tamper-evident JSON record chain")
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("demo.json"))
    parser.add_argument("--verify", action="store_true", help="Treat input as an already built chain")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if args.verify:
            if not verify_chain(data):
                parser.exit(1, "Chain verification FAILED\n")
            print("Chain verification PASSED")
        else:
            chain = build_chain(data)
            print(json.dumps({"status": "local-demo-only", "valid": verify_chain(chain), "blocks": chain}, indent=2))
    except (ChainError, OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        parser.exit(2, f"Chainlab input error: {exc}\n")


if __name__ == "__main__":
    main()
