"""
test_osworld.py  —  verify screenshot + accessibility tree from a running OSWorld VM.

Run from the REPO ROOT (G:\\LabWork\\ProjectPRM):
    python scripts/test_osworld.py
    python scripts/test_osworld.py --provider docker
    python scripts/test_osworld.py --provider vmware --path_to_vm "E:\\OSWorld\\VM\\Ubuntu.vmx"

Outputs are saved to:
    results/test/obs_screenshot.png
    results/test/obs_a11y_tree.xml  (or .txt)

Note: DesktopEnv always captures both screenshot and a11y tree — observation_type
is an agent-level concept and is NOT passed to DesktopEnv here.
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

# ── Paths — never chdir, always use absolute references ──────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent   # G:\LabWork\ProjectPRM
OSWORLD_DIR = REPO_ROOT / "benchmarks" / "OSWorld"
OUT_DIR     = REPO_ROOT / "results" / "test"

if not OSWORLD_DIR.exists():
    sys.exit(f"ERROR: OSWorld submodule not found at {OSWORLD_DIR}")

# Add OSWorld to path WITHOUT changing the working directory
if str(OSWORLD_DIR) not in sys.path:
    sys.path.insert(0, str(OSWORLD_DIR))

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Test OSWorld screenshot + a11y tree extraction")
parser.add_argument("--provider",   default="docker", help="docker or vmware (default: docker)")
parser.add_argument("--path_to_vm", default=None,     help="Path to .vmx file (vmware only)")
args = parser.parse_args()

# ── Ensure output directory exists ────────────────────────────────────────────
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Import DesktopEnv without polluting the working directory ─────────────────
# We temporarily chdir only for the import since OSWorld hard-codes relative
# config paths, then immediately restore the original cwd.
_orig_cwd = os.getcwd()
os.chdir(OSWORLD_DIR)
try:
    from desktop_env.desktop_env import DesktopEnv
finally:
    os.chdir(_orig_cwd)

# ── Minimal task — boots to desktop, no real evaluation ───────────────────────
TASK = {
    "id": "obs_test",
    "instruction": "observation test — screenshot and accessibility tree check",
    "config": [],
    "evaluator": {
        "func": "check_include_exclude",
        "result":   {"type": "vm_command_line", "command": "echo ok"},
        "expected": {"include": ["ok"]},
        "options":  {}
    }
}

# ── Boot VM ───────────────────────────────────────────────────────────────────
print(f"Repo root    : {REPO_ROOT}")
print(f"OSWorld dir  : {OSWORLD_DIR}")
print(f"Output dir   : {OUT_DIR}")
print(f"Provider     : {args.provider}")
if args.path_to_vm:
    print(f"VM path      : {args.path_to_vm}")
print("\nBooting VM (this may take 30–90 s on first run)...\n")

env_kwargs = dict(provider_name=args.provider)
if args.path_to_vm:
    env_kwargs["path_to_vm"] = args.path_to_vm

env = DesktopEnv(**env_kwargs)
obs = env.reset(task_config=TASK)

print("env.reset() complete.")
print("Observation keys:", list(obs.keys()), "\n")

# ── 1. Screenshot ─────────────────────────────────────────────────────────────
screenshot_data = obs.get("screenshot")

if screenshot_data is None:
    print("❌  screenshot : None (key missing from observation)")
else:
    from PIL import Image

    if isinstance(screenshot_data, bytes):
        # Raw PNG/JPEG bytes
        img = Image.open(io.BytesIO(screenshot_data))
    elif isinstance(screenshot_data, str):
        # base64-encoded string
        img = Image.open(io.BytesIO(base64.b64decode(screenshot_data)))
    else:
        img = screenshot_data  # already a PIL Image

    img_path = OUT_DIR / "obs_screenshot.png"
    img.save(img_path)
    print(f"✅  screenshot  {img.size[0]}x{img.size[1]} px  →  {img_path}")

# ── 2. Accessibility tree ─────────────────────────────────────────────────────
a11y = (obs.get("accessibility_tree")
     or obs.get("a11y_tree")
     or obs.get("dom"))

if a11y is None:
    print("   a11y not in reset() obs — sending a no-op step to trigger it...")
    obs2, _, _, _ = env.step("MOVE_TO(100, 100)")
    a11y = (obs2.get("accessibility_tree")
         or obs2.get("a11y_tree")
         or obs2.get("dom"))

if a11y is None:
    print("❌  accessibility_tree : None (not found in obs or step obs)")
    print("   Available keys:", list(obs.keys()))
else:
    if isinstance(a11y, bytes):
        a11y = a11y.decode("utf-8", errors="replace")

    is_xml  = a11y.lstrip().startswith("<")
    ext     = "xml" if is_xml else "txt"
    a11y_path = OUT_DIR / f"obs_a11y_tree.{ext}"
    a11y_path.write_text(a11y, encoding="utf-8")
    print(f"✅  accessibility_tree ({ext})  {len(a11y):,} chars  →  {a11y_path}")

    print("\n── First 20 lines ──────────────────────────────────────────────────")
    for line in a11y.splitlines()[:20]:
        print(" ", line[:120])
    total = len(a11y.splitlines())
    if total > 20:
        print(f"  ... ({total} lines total)")

# ── 3. Full observation summary ───────────────────────────────────────────────
print("\n── All observation fields ──────────────────────────────────────────")
for k, v in obs.items():
    if v is None:
        desc = "None"
    elif isinstance(v, str):
        desc = f"str  {len(v):,} chars"
    elif isinstance(v, bytes):
        desc = f"bytes  {len(v):,} bytes"
    else:
        desc = f"{type(v).__name__}  {repr(v)[:60]}"
    print(f"  {k:<28} {desc}")

# ── Cleanup ───────────────────────────────────────────────────────────────────
env.close()
print(f"\n✅  Done — all outputs saved to {OUT_DIR}")