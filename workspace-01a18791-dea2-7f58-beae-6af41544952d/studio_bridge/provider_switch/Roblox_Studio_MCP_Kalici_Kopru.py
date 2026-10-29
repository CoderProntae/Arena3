#!/usr/bin/env python3
"""Windows Studio MCP client; encrypted ntfy.envs.net mailbox, no inbound tunnel.

Run ONLY on your own Windows PC. It starts the Roblox-provided local mcp.bat
and makes outbound HTTPS requests. It does not open a server port or ask for
Roblox credentials. The user must type YES separately for EACH mutating tool.
Provider switch after old host daily quota reached. Same local-YES safeguard;
keep all three package files together. Ctrl+C to disconnect.
"""
from __future__ import annotations

import json
import os
import platform
import queue
import secrets
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from Roblox_Studio_Bus import BusError, EncryptedBus

READ_TOOLS = frozenset({
    "list_roblox_studios", "get_studio_state", "search_game_tree",
    "inspect_instance", "script_search", "script_grep", "script_read",
    "get_console_output", "screen_capture",
})
APPROVAL_TOOLS = frozenset({
    "start_stop_play", "execute_luau", "multi_edit", "character_navigation",
    "user_mouse_input", "user_keyboard_input",
})
ALLOWED_TOOLS = READ_TOOLS | APPROVAL_TOOLS
MAX_TOOL_REQUEST = 14_000_000


class MCPError(RuntimeError):
    pass


class StdioMCPClient:
    def __init__(self, command: list[str], cwd: Path | None = None):
        self.command = command
        self.cwd = cwd
        self.process = None
        self.pending: dict[int, queue.Queue] = {}
        self.lock = threading.Lock()
        self.next_id = 0
        self.tools: list[dict] = []

    def start(self):
        self.process = subprocess.Popen(
            self.command, cwd=self.cwd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
        )
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._stderr_reader, daemon=True).start()
        initialized = False
        for version in ("2025-06-18", "2025-03-26", "2024-11-05"):
            response = self.request("initialize", {
                "protocolVersion": version, "capabilities": {},
                "clientInfo": {"name": "Arena-User-Operated-Encrypted-MCP",
                               "version": "1.1.0"},
            }, timeout=70)
            if "result" in response:
                initialized = True
                break
            print("[MCP] Initialization refused:", str(response.get("error"))[:280])
        if not initialized:
            raise MCPError("Roblox Studio MCP refused the initialize handshake")
        self.notify("notifications/initialized", {})
        cursor = None
        for _ in range(12):
            response = self.request("tools/list", {"cursor": cursor} if cursor else {},
                                    timeout=60)
            if "error" in response:
                raise MCPError("tools/list: " + str(response["error"])[:500])
            result = response.get("result") or {}
            tools = result.get("tools")
            if not isinstance(tools, list):
                raise MCPError("Studio did not provide valid tool definitions")
            self.tools.extend(x for x in tools if isinstance(x, dict))
            cursor = result.get("nextCursor")
            if not cursor:
                break
        print(f"[MCP] Connected. Server advertises {len(self.tools)} tools.")

    def _stderr_reader(self):
        assert self.process and self.process.stderr
        for line in self.process.stderr:
            text = line.strip()
            if text:
                print("[Studio MCP stderr]", text[:350])

    def _reader(self):
        assert self.process and self.process.stdout
        for raw in self.process.stdout:
            try:
                message = json.loads(raw.strip())
            except json.JSONDecodeError:
                if raw.strip():
                    print("[Studio MCP stdout]", raw.strip()[:250])
                continue
            if not isinstance(message, dict):
                continue
            identifier = message.get("id")
            if identifier is not None and ("result" in message or "error" in message):
                with self.lock:
                    channel = self.pending.pop(identifier, None)
                if channel:
                    channel.put(message)
            elif identifier is not None and "method" in message:
                response = {"jsonrpc": "2.0", "id": identifier}
                if message["method"] == "ping":
                    response["result"] = {}
                else:
                    response["error"] = {"code": -32601,
                                         "message": "Client method not available"}
                self._send(response)
        print("[MCP] Studio MCP subprocess disconnected.")

    def _send(self, obj: dict):
        if not self.process or self.process.poll() is not None or not self.process.stdin:
            raise MCPError("Studio MCP subprocess has stopped")
        payload = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        if len(payload.encode("utf-8")) > MAX_TOOL_REQUEST:
            raise MCPError("Request larger than 14 MB is refused")
        with self.lock:
            self.process.stdin.write(payload + "\n")
            self.process.stdin.flush()

    def request(self, method: str, params: dict, timeout: int = 150) -> dict:
        channel: queue.Queue = queue.Queue(maxsize=1)
        with self.lock:
            self.next_id += 1
            identifier = self.next_id
            self.pending[identifier] = channel
        try:
            self._send({"jsonrpc": "2.0", "id": identifier,
                        "method": method, "params": params})
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                if self.process and self.process.poll() is not None:
                    raise MCPError(f"Studio MCP exited: {self.process.returncode}")
                try:
                    return channel.get(timeout=min(2, max(0.01, end-time.monotonic())))
                except queue.Empty:
                    continue
            raise MCPError(f"Studio {method} timed out after {timeout}s")
        finally:
            with self.lock:
                self.pending.pop(identifier, None)

    def notify(self, method: str, params: dict):
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def close(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()


def local_approval(tool: str, arguments: dict) -> bool:
    text = json.dumps(arguments, ensure_ascii=False, indent=2)
    print("\n" + "=" * 62)
    print("STUDIO ACTION REQUIRES USER APPROVAL / KULLANICI ONAYI GEREKLI")
    print("Requested tool:", tool)
    print("Arguments (first 1200 characters):\n" + text[:1200])
    review_path = None
    if len(text) > 1200:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                suffix=".json", prefix="arena_studio_review_",
                delete=False) as temp:
            temp.write(text)
            review_path = Path(temp.name)
        print("Full arguments for review:", review_path)
        print("Open the file before approval. It is deleted after the answer.")
    print("Press Enter to DENY if you did not request this action.")
    try:
        answer = input("Approve THIS ONE Studio operation? Type YES: ").strip()
    finally:
        if review_path:
            review_path.unlink(missing_ok=True)
    print("=" * 62)
    return answer == "YES"


def announce_with_retries(bus: EncryptedBus, hello: dict) -> None:
    for attempt in range(1, 9):
        try:
            bus.publish(bus.responses, hello)
            return
        except BusError as exc:
            if attempt == 8:
                raise MCPError("Encrypted HTTPS mailbox could not register") from exc
            print(f"[bridge] HTTPS mailbox unavailable: {exc}; retrying ({attempt}/8)")
            time.sleep(min(12, attempt * 2))


def run_worker(studio: StdioMCPClient, bus: EncryptedBus) -> None:
    session = secrets.token_hex(16)
    advertised = {x.get("name"): x for x in studio.tools
                  if x.get("name") in ALLOWED_TOOLS}
    hello = {"kind": "HELLO", "session": session,
             "tools": list(advertised.values()), "time": time.time()}
    announce_with_retries(bus, hello)
    print(f"[bridge] ONLINE via encrypted HTTPS mailbox; {len(advertised)} supported tools.")
    print("[bridge] Leave this console open and tell the agent: Kopru ONLINE")
    print("[bridge] Ctrl+C disconnects; read-only access is active.\n")
    cursor = "all"
    processed: set[str] = set()
    network_errors = 0
    next_hello = time.monotonic() + 240
    while True:
        if studio.process and studio.process.poll() is not None:
            raise MCPError("Studio MCP stopped. Check whether Studio is still open.")
        if time.monotonic() >= next_hello:
            # Re-advertise liveness after a transient network interruption.
            try:
                bus.publish(bus.responses, hello | {"time": time.time()})
                next_hello = time.monotonic() + 240
            except BusError as exc:
                print("[bridge] Heartbeat could not be sent:", exc)
                next_hello = time.monotonic() + 25
        try:
            calls, cursor = bus.read(bus.commands, cursor)
            network_errors = 0
        except BusError as exc:
            network_errors += 1
            print("[bridge] Temporary community HTTPS problem:", exc)
            time.sleep(min(32, 6 + network_errors * 3))
            continue
        for call in calls:
            if call.get("kind") != "CALL" or call.get("session") != session:
                continue
            job = call.get("job")
            tool = call.get("tool")
            arguments = call.get("arguments")
            timestamp = call.get("time")
            if (not isinstance(job, str) or not isinstance(tool, str)
                or not isinstance(arguments, dict) or not isinstance(timestamp, (int, float))
                or job in processed or time.time() - timestamp > 900
                or timestamp - time.time() > 120):
                continue
            processed.add(job)
            try:
                if tool not in advertised:
                    raise MCPError("Tool not supported by local allowlist or MCP server")
                if tool in APPROVAL_TOOLS and not local_approval(tool, arguments):
                    raise MCPError("User denied this Studio operation")
                print("[bridge] Studio tool:", tool)
                output = studio.request("tools/call",
                                        {"name": tool, "arguments": arguments},
                                        timeout=180)
                result = {"kind": "RESULT", "session": session,
                          "job": job, "tool": tool,
                          "ok": "error" not in output,
                          "response": output, "time": time.time()}
            except (MCPError, ValueError, OSError) as exc:
                result = {"kind": "RESULT", "session": session,
                          "job": job, "tool": tool, "ok": False,
                          "response": {"error": str(exc)}, "time": time.time()}
            try:
                bus.publish(bus.responses, result)
                print("[bridge] Returned result for:", tool)
            except BusError as exc:
                # Do not retry possibly mutating calls: result may already
                # have been posted. The user can report the console output.
                print("[bridge] Could not publish result:", exc)
        time.sleep(11)


def main() -> None:
    if platform.system() != "Windows":
        raise MCPError("Run on the Windows PC where Roblox Studio is installed")
    app = os.environ.get("LOCALAPPDATA")
    if not app:
        raise MCPError("Windows LOCALAPPDATA not found")
    folder = Path(app) / "Roblox"
    launcher = folder / "mcp.bat"
    if not launcher.is_file():
        raise MCPError(f"Studio MCP launcher not found: {launcher}")
    config_path = Path(__file__).with_name("Roblox_Studio_MCP_Gizli_Ayar.json")
    if not config_path.is_file():
        raise MCPError(f"Secret configuration missing: {config_path}")
    bus = EncryptedBus.from_file(config_path)
    print("[bridge] Studio MCP launcher:", launcher)
    print("[bridge] Encrypted outbound-only mailbox: https://ntfy.envs.net")
    print("[bridge] No incoming port/tunnel. Ctrl+C stops access.")
    print("[bridge] Play, Luau, edits and player input require local YES per call.")
    print("[bridge] Third-party mailbox: avoid confidential Studio windows. Do not share the secret JSON.\n")
    studio = StdioMCPClient(["cmd.exe", "/d", "/c", ".\\mcp.bat"], cwd=folder)
    try:
        studio.start()
        run_worker(studio, bus)
    finally:
        studio.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bridge] Disconnected on user request.")
    except (MCPError, BusError, OSError) as exc:
        print("\n[bridge] ERROR:", exc)
        sys.exit(1)
