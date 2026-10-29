#!/usr/bin/env python3
"""Agent-side encrypted HTTPS mailbox control; not a Roblox Studio connector.

No process is left listening after each command. Both agents poll ntfy.sh on
outbound HTTPS; the Windows-side user must explicitly run their client.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
from pathlib import Path

from Roblox_Studio_Bus import BusError, EncryptedBus

HERE = Path(__file__).resolve().parent
CONFIG = Path(os.environ.get("STUDIO_BUS_CONFIG", str(HERE / "Roblox_Studio_MCP_Gizli_Ayar.json")))
JOBS = HERE / "community_jobs.json"
RESULTS = HERE / "community_results"
ACTIVE = HERE / ("community_active_hello_test.json" if "STUDIO_BUS_CONFIG" in os.environ
                 else "community_active_hello.json")
RESULTS.mkdir(exist_ok=True)
BUS = EncryptedBus.from_file(CONFIG)


def latest_hello() -> dict | None:
    # A public ntfy topic has strict request and replay quotas. Cache the
    # last authenticated worker HELLO instead of fetching all 28 schemas
    # every time we call one MCP tool (which exhausted the free rate limit).
    cached = None
    if ACTIVE.exists():
        try:
            cached = json.loads(ACTIVE.read_text(encoding="utf-8"))
            if time.time() - float(cached.get("_ntfy_time") or 0) < 260:
                return cached
        except (ValueError, OSError, TypeError):
            cached = None
    try:
        messages, _ = BUS.read(BUS.responses, str(max(0, int(time.time()) - 420)))
    except BusError:
        if cached and time.time() - float(cached.get("_ntfy_time") or 0) < 350:
            return cached
        raise
    hellos = [x for x in messages if x.get("kind") == "HELLO"
              and isinstance(x.get("session"), str)]
    if hellos:
        latest = max(hellos, key=lambda x: x.get("_ntfy_time") or 0)
        ACTIVE.write_text(json.dumps(latest, ensure_ascii=False), encoding="utf-8")
        ACTIVE.chmod(0o600)
        return latest
    return cached if cached and time.time() - float(cached.get("_ntfy_time") or 0) < 350 else None


def load_jobs() -> dict:
    return json.loads(JOBS.read_text(encoding="utf-8")) if JOBS.exists() else {}


def save_jobs(value: dict) -> None:
    JOBS.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    JOBS.chmod(0o600)


def paths_for_images(obj: object, job: str) -> list[str]:
    paths = []
    def visit(value: object, depth: int = 0):
        if depth > 12 or len(paths) >= 8:
            return
        if isinstance(value, list):
            for x in value:
                visit(x, depth + 1)
        elif isinstance(value, dict):
            if value.get("type") == "image" or str(value.get("mimeType", "")).startswith("image/"):
                data = value.get("data")
                if isinstance(data, str):
                    try:
                        blob = base64.b64decode(data, validate=True)
                        if len(blob) > 12_000_000:
                            return
                        if blob.startswith(b"\x89PNG\r\n\x1a\n"):
                            suffix = ".png"
                        elif blob.startswith(b"\xff\xd8\xff"):
                            suffix = ".jpg"
                        else:
                            return
                        path = RESULTS / f"{job}_{len(paths)+1}{suffix}"
                        path.write_bytes(blob)
                        paths.append(str(path))
                    except (ValueError, base64.binascii.Error):
                        return
            for key, item in value.items():
                if key not in {"data", "text"}:
                    visit(item, depth + 1)
    visit(obj)
    return paths


def get_result(job: str) -> dict:
    jobs = load_jobs()
    if job not in jobs:
        raise BusError("Unknown job ID; only previously created jobs can be retrieved")
    output = RESULTS / f"{job}.json"
    if output.exists():
        result = json.loads(output.read_text(encoding="utf-8"))
        existing_images = [str(p) for p in RESULTS.glob(f"{job}_*.*")]
        return {"id": job, "status": "done", "tool": jobs[job]["tool"],
                "ok": result.get("ok"), "response_file": str(output),
                "images": existing_images}
    # Query messages published AFTER this job was queued. Polling since=all
    # repeatedly would re-download every old screenshot and exhaust quotas.
    since = str(max(0, int(jobs[job]["queued"]) - 3))
    events, _ = BUS.read(BUS.responses, since)
    matching = [x for x in events if x.get("kind") == "RESULT"
                and x.get("job") == job
                and x.get("session") == jobs[job]["session"]]
    if not matching:
        return {"id": job, "status": "pending", "tool": jobs[job]["tool"]}
    result = matching[-1]
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    images = paths_for_images(result.get("response"), job)
    return {"id": job, "status": "done", "tool": jobs[job]["tool"],
            "ok": result.get("ok"), "response_file": str(output),
            "images": images}


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: status | tools | schema NAME | call NAME [JSON or @file] | result JOB | wait JOB [seconds]")
    action = sys.argv[1]
    if action in ("status", "tools", "schema", "call"):
        hello = latest_hello()
        if not hello:
            print(json.dumps({"status": "no_worker_hello", "action": action}))
            return
        age = time.time() - float(hello.get("_ntfy_time") or 0)
        tools = [x for x in hello.get("tools", []) if isinstance(x, dict)]
        names = [x.get("name") for x in tools]
        if action == "status":
            info = {"status": "recent" if age < 260 else "stale",
                    "last_hello_age_seconds": round(age, 1),
                    "session": hello["session"], "tool_count": len(tools),
                    "tool_names": names}
        elif action == "tools":
            file = RESULTS / "studio_tools.json"
            file.write_text(json.dumps(tools, indent=2, ensure_ascii=False),
                            encoding="utf-8")
            info = {"tool_count": len(tools), "names": names,
                    "schemas_file": str(file)}
        elif action == "schema":
            if len(sys.argv) < 3:
                raise SystemExit("schema NAME")
            info = next((t for t in tools if t.get("name") == sys.argv[2]),
                        {"error": "not advertised"})
        else:
            if len(sys.argv) < 3:
                raise SystemExit("call NAME [JSON or @file]")
            name = sys.argv[2]
            if name not in names:
                raise BusError("Tool not in previously advertised local list")
            if age >= 260:
                raise BusError("Worker heartbeat is stale; do not queue Studio modifications")
            raw = sys.argv[3] if len(sys.argv) > 3 else "{}"
            if raw.startswith("@"):
                raw = Path(raw[1:]).read_text(encoding="utf-8")
            args = json.loads(raw)
            if not isinstance(args, dict):
                raise BusError("Tool arguments must be a JSON object")
            job = uuid.uuid4().hex
            BUS.publish(BUS.commands, {"kind": "CALL", "job": job,
                       "session": hello["session"], "tool": name,
                       "arguments": args, "time": time.time()})
            jobs = load_jobs()
            jobs[job] = {"session": hello["session"],
                         "tool": name, "queued": time.time()}
            save_jobs(jobs)
            info = {"job": job, "tool": name,
                    "requires_local_yes": name not in {
                        "list_roblox_studios", "get_studio_state",
                        "search_game_tree", "inspect_instance",
                        "script_search", "script_grep", "script_read",
                        "get_console_output", "screen_capture"}}
    elif action in ("result", "wait"):
        if len(sys.argv) < 3:
            raise SystemExit("result JOB | wait JOB [seconds]")
        job = sys.argv[2]
        if action == "result":
            info = get_result(job)
        else:
            max_seconds = max(1, min(int(sys.argv[3]) if len(sys.argv) > 3 else 75, 150))
            deadline = time.monotonic() + max_seconds
            while True:
                try:
                    info = get_result(job)
                except BusError as exc:
                    # Public ntfy may briefly rate-limit HTTPS polling. Do
                    # not retry every 4 seconds or lose the command result.
                    print(f"community provider cooldown while waiting for {job}: {exc}",
                          file=sys.stderr)
                    info = {"id": job, "status": "pending"}
                    time.sleep(12)
                if info["status"] == "done" or time.monotonic() >= deadline:
                    break
                time.sleep(11)
    else:
        raise SystemExit("Unknown action")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BusError as error:
        raise SystemExit(f"BROKER ERROR: {error}") from error
