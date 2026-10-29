#!/usr/bin/env python3
"""Checkpoint 05 reproducible Studio Play evidence check (V16 magnetically confined fusion sun; pending separate user visual decision)."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / "reactor_startup/qa"
PARSER = ROOT / ".cache/luau/luau-compile"

FILES = [
    ROOT / "reactor_startup/source/ReactorPilot_SixHeads.server.lua",
    ROOT / "reactor_startup/source/ReactorPilot_CustomFlow.server.lua",
    ROOT / "reactor_startup/source/ReactorPilot_CustomVapor.client.lua",
    ROOT / "CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua",
    ROOT / "model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua",
    ROOT / "CORE_PROTOCOL_REMAKE_Client.client.lua",
]
for path in FILES:
    assert path.exists(), path
    if PARSER.exists():
        p = subprocess.run([str(PARSER), "--only-parse", str(path)], capture_output=True, text=True)
        assert p.returncode == 0, (path, p.stderr)

# Prior approvals 01-04 must exist
for filename, key in [
    ("checkpoint01_approval.json", "user_selected"),
    ("checkpoint02_approval.json", "accepted"),
    ("checkpoint03_approval.json", "accepted"),
    ("checkpoint04_approval.json", "accepted"),
]:
    d = json.loads((QA / filename).read_text())
    assert d[key] in (True, "approve"), filename

pilot = FILES[0].read_text()
server = FILES[3].read_text()
assert "WHITE_PLASMA_HOLD_FOR_USER_APPROVAL" in pilot
assert 'Instance.new("Part")' not in pilot and 'Instance.new("MeshPart")' not in pilot
assert 'Instance.new("Sound")' not in pilot
assert 'SetAttribute("ReactorMode","ONLINE")' not in pilot
assert "p.Transparency=1-mesh.opacity*volume*(1-white)" in pilot
assert "edgeZero=1-soft(.75,.97,radius)" in pilot
assert "sunGuard=1-soft(.62,.90,radius)" in pilot
assert "SILENT_PROTOTYPE=true" in server
assert "STUDIO_AUTO_STARTUP=false" in server

j = json.loads((QA / "checkpoint05_jobs.json").read_text())
for name in (
    "white_nebula_volume_v11", "white_radiant_plasma_v12", "white_cobalt_contrast_v13",
    "white_magnetic_star_v14", "white_balanced_star_v15", "white_round_sun_v16",
    "test_auto_off", "verify_auto_off",
):
    assert j[name]["done"] is True, name

readback = json.loads(Path(j["verify_auto_off"]["response"]).read_text())["response"]["result"]
readtext = "\n".join(x.get("text", "") for x in readback["content"] if x["type"] == "text")
assert readback["isError"] is False
assert "STUDIO_AUTO_STARTUP=false" in readtext and "STUDIO_AUTO_STARTUP=true" not in readtext

cold_doc = json.loads((QA / "checkpoint05_cold_final_attr.json").read_text())
for k in ("auto_off", "verify_script", "cold_start", "cold_world", "cold_stop", "final_state"):
    assert cold_doc[k]["ok"] is True, k
cold = cold_doc["cold_attributes"]
assert cold["ReactorMode"] == "COLD" and cold["ReactorPilotDarkness"] == 0
for k in (
    "ReactorPilotRelayMask", "ReactorPilotPhotonSources", "ReactorPilotCoreMeshActive",
    "ReactorPilotCyanVolume", "ReactorPilotWhiteVolume", "ReactorPilotWhiteVfxBeams",
    "ReactorPilotWhiteWispSources", "ReactorPilotWhiteCurvedArcs", "ReactorPilotFuelNozzles",
    "ReactorPilotNewVisibleParts",
):
    assert cold[k] == 0, (k, cold[k])

W = json.loads((QA / "checkpoint05_round_sun_v16_play.json").read_text())
for k in ("edit_pilot_v16", "start", "frame_t1", "frame_t2", "world", "console", "stop"):
    assert W[k]["done"] is True, k
w_res = json.loads(Path(W["world"]["response"]).read_text())["response"]["result"]
assert w_res["isError"] is False
white = json.loads(next(x["text"] for x in w_res["content"] if x["type"] == "text"))["attributes"]
assert white["ReactorMode"] == "STARTUP" and white["ReactorStartupAge"] > 60
assert white["ReactorPilotStage"] == "WHITE_PLASMA_HOLD_FOR_USER_APPROVAL"
assert white["ReactorPilotRelayMask"] == 63
assert white["ReactorPilotPhotonSources"] == 6
assert white["ReactorPilotCoreMeshActive"] == 0
assert white["ReactorPilotWhiteVfxBeams"] == 7
assert white["ReactorPilotWhiteWispSources"] == 14
assert white["ReactorPilotWhiteCurvedArcs"] == 0
assert white["ReactorPilotWhiteVolume"] == 1
assert white["ReactorPilotWhiteTexture"] == "PROCEDURAL_REPLICATED_CONTENT"
assert white["ReactorPilotSunTexture"] == "PROCEDURAL_SUN_OK"
assert white["ReactorPilotNewVisibleParts"] == 0
assert white["SilentPrototype"] is True

img_report = ROOT / "reports/KONTROL_05_EFEKT_BAZLI_BEYAZ_PLAZMA_PLAY.jpg"
raw_t1 = Path(W["frame_t1"]["images"][0])
raw_t2 = Path(W["frame_t2"]["images"][0])
assert img_report.read_bytes() == raw_t1.read_bytes()
assert hashlib.sha256(img_report.read_bytes()).hexdigest() == "9c8a5422c54812de23564e47fb06d7cd3b8346dfaedcbe469ce46994f9de98c2"

arr1 = np.asarray(Image.open(raw_t1).convert("RGB"), dtype=np.float32)
arr2 = np.asarray(Image.open(raw_t2).convert("RGB"), dtype=np.float32)
assert arr1.shape == arr2.shape and arr1.shape[0] >= 700 and arr1.shape[1] >= 750
mad = float(np.mean(np.abs(arr1 - arr2)))
assert mad < 1.5, f"Unstable/chaotic motion detected between T1 and T2: {mad:.2f}"

h, w = arr1.shape[:2]
roi = arr1[135:515, int(w * 0.24):int(w * 0.76)]
lum = roi.mean(axis=2)
clip252 = float(np.mean(np.all(roi > 252, axis=2)))
lum220 = float((lum > 220).mean())
blue_field = float(np.mean((roi[:, :, 2] > roi[:, :, 0] * 1.25) & (roi[:, :, 2] > 60) & (lum < 225)))
assert clip252 < 0.09 and lum220 > 0.12 and blue_field > 0.40

# Persistable workspace budget check (<128 MB)
EXCLUDED_DIRS = {
    ".arena", ".cache", ".local", ".mypy_cache", ".next", ".nox", ".npm", ".nuxt",
    ".output", ".parcel-cache", ".playwright-cli", ".pytest_cache", ".ruff_cache",
    ".svelte-kit", ".tox", ".turbo", ".venv", ".vite", "__pycache__", "build",
    "coverage", "dist", "node_modules", "out", "target",
}
persist_files = [
    p for p in ROOT.rglob("*")
    if p.is_file() and not any(part in EXCLUDED_DIRS for part in p.relative_to(ROOT).parts)
]
total_bytes = sum(p.stat().st_size for p in persist_files)
mib = total_bytes / (1024 * 1024)
assert mib < 124.0 and len(persist_files) < 9500, f"Budget risk: {mib:.2f} MiB, {len(persist_files)} files"

print("PASS six Luau scripts parse; 01-04 approvals intact; 05 holds before ONLINE")
print("PASS COLD regression 0 relay/laser/white/fuel; Studio STUDIO_AUTO_STARTUP=false & Edit state verified")
print(f"PASS V16 Studio Play T1/T2 stability: MAD={mad:.2f}/255, lum>220={lum220:.1%}, cobalt-blue field={blue_field:.1%}")
print(f"PASS persistable workspace budget: {mib:.2f} MiB, {len(persist_files)} files (< 128 MB / 10,000 files)")
print("PENDING separate user visual decision for Checkpoint 05; will STOP at 05 even if approved.")
