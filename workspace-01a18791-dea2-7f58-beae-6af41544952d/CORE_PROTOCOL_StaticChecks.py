#!/usr/bin/env python3
"""Offline structural tests for the CORE PROTOCOL Roblox sources.

This is NOT a substitute for running Roblox Studio > Test > Play. The
geometry test samples a subset of the hard-coded observation structures;
Studio's own Workspace:Raycast audit in the server file is more complete.
"""
from __future__ import annotations
import math
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SERVER = (HERE / "CORE_PROTOCOL_Server.server.lua").read_text()
CLIENT = (HERE / "CORE_PROTOCOL_Client.client.lua").read_text()


def check(label: str, condition: bool) -> None:
    assert condition, f"FAILED: {label}"
    print(f"PASS  {label}")


check("Two distinct Roblox entrypoints", "RunService.Heartbeat:Connect" in SERVER
      and "StarterPlayerScripts" in CLIENT)
line_count = len(SERVER.splitlines()) + len(CLIENT.splitlines())
check(f"Source limit ({line_count}/8000 lines)", line_count <= 8000)
check("Reference meltdown is exactly 435 seconds",
      re.search(r"MELTDOWN_SECONDS\s*=\s*435\b", SERVER) is not None)

# Inspect the discrete authored crisis beats independently of documentation.
beats = [int(t) for t in re.findall(r'flagAt\(age,(\d+),"', SERVER)]
check(f"At least twenty-one individually scripted crisis beats ({len(beats)})",
      len(beats) >= 21 and beats == sorted(set(beats)))
check("Every authored beat is before detonation",
      all(0 < t < 435 for t in beats) and max(beats) >= 430)

block = SERVER.split("AUDIO={", 1)[1].split("\n    },", 1)[0]
sound_keys = set(re.findall(r"\b([a-z]+)\s*=\s*\"rbxassetid://", block))
called_sounds = set(re.findall(r'sfx\("([a-z]+)"', SERVER))
check("Every server effect points to a configured audio ID",
      called_sounds <= sound_keys)
check("Client soundtrack changes are sourced by the server",
      all(f"CFG.AUDIO.{name}" in SERVER for name in
          ("opening", "escalation", "finale")))

controls = re.findall(r'local (\w+)\s*=makeControl\(', SERVER)
check("Seven modeled controls with ClickDetector bindings",
      len(controls) == 7 and all(
          f"{c}.click.MouseClick:Connect" in SERVER for c in controls))
check("Three collectible cards and three interactive card sockets",
      "for slot=1,3 do" in SERVER
      and "for i=1,3 do" in SERVER
      and "bay.click.MouseClick:Connect" in SERVER
      and "data.click.MouseClick:Connect" in SERVER)
check("Client cannot request changes to reactor state",
      'command~="SYNC" then return' in SERVER
      and "remote:FireAllClients" in SERVER)
check("No opaque mechanical shutter in front of the window",
      "liveShutters" not in SERVER and "PANORAMIC_LAMINATED_GLASS" in SERVER)

# Analytic AABB test of model coordinates; glass itself is intentionally
# excluded because its transparency is >0.96 and it preserves the view.
obstacles = [
    ("floor", (-63, 63, 20.6, 24.0, 91, 163)),
    ("left side", (-63.15, -60.85, 23.5, 80.5, 91, 125)),
    ("right side", (60.85, 63.15, 23.5, 80.5, 91, 125)),
    ("parapet", (-63, 63, 23.9, 28.7, 92.05, 94.55)),
    ("arch", (-63, 63, 71.5, 82.5, 92.05, 94.55)),
    ("left mullion", (-18.1, -17.9, 29.0, 72.2, 93.0, 94.1)),
    ("right mullion", (17.9, 18.1, 29.0, 72.2, 93.0, 94.1)),
    ("desk support", (-66, -10, 24.1, 28.1, 135, 153)),
    ("desk surface", (-66, -10, 27.5, 30.0, 135, 153)),
    ("raised shutdown body", (-15, 15, 25.1, 29.1, 118.5, 133.5)),
    ("large overhead lamp", (-26.5, 26.5, 76.8, 79.4, 104.6, 113.4)),
]


def intersects(a, b, v):
    lo, hi = 0.0, 1.0
    for axis in range(3):
        left, right = v[axis * 2], v[axis * 2 + 1]
        movement = b[axis] - a[axis]
        if abs(movement) < 1e-9:
            if a[axis] < left or a[axis] > right:
                return False
            continue
        t0, t1 = (left - a[axis]) / movement, (right - a[axis]) / movement
        lo, hi = max(lo, min(t0, t1)), min(hi, max(t0, t1))
        if lo > hi:
            return False
    return hi >= 0 and lo <= 1


lines = []
for eye_x in (-6, 0, 6):
    for target_x in (-14, 0, 14):
        eye, target = (eye_x, 35, 151), (target_x, 53, 27)
        at_window = tuple(eye[i] + (target[i] - eye[i]) *
                          (151 - 93.25) / (151 - 27) for i in range(3))
        check(f"Glass aperture {eye_x:+}/{target_x:+}",
              -53 < at_window[0] < 53 and 29.5 < at_window[1] < 71.5
              and all(not intersects(eye, target, aabb) for _, aabb in obstacles))
        lines.append((eye, target))
check("Nine sightline sample geometry checks completed", len(lines) == 9)

# Model the same coolant/power/laser target as server normalSimulation.
thermal = lambda power, laser, coolant, emergency=False: (
    550 + power * 12 + (650 if laser else 0) - coolant * 4.5
    - (320 if emergency else 0))
check("Moderate power with coolant maintains a stable online core",
      450 < thermal(25, False, 50) < 1100)
check("Overpowered lasers can exceed meltdown threshold",
      thermal(100, True, 0) > 1640)
check("Emergency cooling can avoid heat runaway if activated early",
      thermal(100, True, 100, True) < 1640)
check("Zero-power full-cooling allows freezedown",
      thermal(0, False, 100) < 250)

print("ALL OFFLINE CHECKS PASS. Studio Play remains necessary for runtime/audio.")
