"""Real CLI workflow: create chain, verify trusted tip, reject tampering."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)

def main():
    created = run("chainlab.py", "--input", "demo.json")
    assert created.returncode == 0, created.stderr
    output = json.loads(created.stdout)
    assert output["status"] == "local-demo-only" and output["valid"]
    tip = output["tip_checkpoint"]
    with tempfile.TemporaryDirectory() as tmp:
        chain = Path(tmp) / "chain.json"
        chain.write_text(json.dumps(output["blocks"]))
        verified = run("chainlab.py", "--input", str(chain), "--verify", "--checkpoint", tip)
        assert verified.returncode == 0, verified.stderr
        manipulated = list(output["blocks"])
        manipulated[0] = dict(manipulated[0], record={"event": "tampered"})
        chain.write_text(json.dumps(manipulated))
        rejected = run("chainlab.py", "--input", str(chain), "--verify", "--checkpoint", tip)
        assert rejected.returncode == 1, rejected
        # A separately anchored tip still catches a coherent full-history rewrite.
        from chainlab import build_chain
        chain.write_text(json.dumps(build_chain([{"event": "totally-rewritten"}])))
        assert run("chainlab.py", "--input", str(chain), "--verify", "--checkpoint", tip).returncode == 1
    print("Chainlab real CLI create->checkpoint verify->tamper rejection passed.")

if __name__ == "__main__":
    main()
