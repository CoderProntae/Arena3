#!/usr/bin/env python3
"""Windows-only, user-operated Roblox Studio MCP client for this Arena session.

SECURITY: Review this file before running. It starts only Studio's own
%LOCALAPPDATA%\\Roblox\\mcp.bat, exchanges MCP JSON-RPC over stdio, and
makes OUTBOUND HTTPS requests to a temporary authenticated relay. It does
not open a port on your computer. Read-only Studio tools are permitted;
Play, writing scripts, Luau execution, and simulated input require an
interactive YES confirmation in THIS Windows console for EACH request.
Stop the bridge at any time with Ctrl+C. No Roblox password is requested.
"""
from __future__ import annotations

import json
import os
import platform
import queue
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

# Session-specific values below are generated once by the agent.
# A later tunnel URL can be supplied without downloading a new Python file:
# PowerShell: $env:ARENA_STUDIO_RELAY_URL = 'https://new-url.trycloudflare.com'
RELAY_URL = os.environ.get("ARENA_STUDIO_RELAY_URL") or "https://35c8e6eeb824e3.lhr.life"
ACCESS_TOKEN = "zT0vCSYhxU2PH_p4Nrma9LZCLh-XCS-1diLcrF2WWITQgAudcWRE8X2xRBChefmz"

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
MAX_OUTPUT = 21 * 1024 * 1024


class MCPError(RuntimeError):
    pass


class StdioMCPClient:
    def __init__(self, command: list[str], cwd: Path | None = None) -> None:
        self.command = command
        self.cwd = cwd
        self.process: subprocess.Popen | None = None
        self.pending: dict[int, queue.Queue] = {}
        self.lock = threading.Lock()
        self.next_id = 0
        self.tools: list[dict] = []

    def start(self) -> None:
        self.process = subprocess.Popen(
            self.command, cwd=self.cwd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            bufsize=1, text=True, encoding="utf-8", errors="replace",
            creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
        )
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._stderr_reader, daemon=True).start()
        initialized = None
        for version in ("2025-06-18", "2025-03-26", "2024-11-05"):
            reply = self.request("initialize", {
                "protocolVersion": version,
                "capabilities": {},
                "clientInfo": {"name": "Arena-User-Operated-Studio-Bridge",
                               "version": "1.0.0"},
            }, timeout=70)
            if "result" in reply:
                initialized = reply["result"]
                break
            print("[MCP] Initialize rejected:", str(reply.get("error"))[:280])
        if initialized is None:
            raise MCPError("MCP initialization failed for all supported protocol versions")
        self.notify("notifications/initialized", {})
        cursor = None
        for _ in range(12):
            reply = self.request("tools/list", {"cursor": cursor} if cursor else {}, timeout=60)
            if "error" in reply:
                raise MCPError("tools/list failed: " + str(reply["error"])[:500])
            result = reply.get("result") or {}
            tools = result.get("tools", [])
            if not isinstance(tools, list):
                raise MCPError("tools/list returned an invalid tool list")
            self.tools.extend(t for t in tools if isinstance(t, dict))
            cursor = result.get("nextCursor")
            if not cursor:
                break
        print(f"[MCP] Connected. Server advertises {len(self.tools)} tools.")

    def _stderr_reader(self) -> None:
        assert self.process and self.process.stderr
        for line in self.process.stderr:
            text = line.strip()
            if text:
                print("[Studio MCP stderr]", text[:350])

    def _reader(self) -> None:
        assert self.process and self.process.stdout
        for raw in self.process.stdout:
            line = raw.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                print("[Studio MCP non-JSON output]", line[:230])
                continue
            if not isinstance(message, dict):
                continue
            identifier = message.get("id")
            if identifier is not None and ("result" in message or "error" in message):
                with self.lock:
                    pending = self.pending.pop(identifier, None)
                if pending:
                    pending.put(message)
            elif identifier is not None and "method" in message:
                method = message["method"]
                # MCP servers may ping clients. No sampling, roots, or
                # arbitrary server-initiated operations are offered.
                if method == "ping":
                    self._send({"jsonrpc": "2.0", "id": identifier, "result": {}})
                else:
                    self._send({"jsonrpc": "2.0", "id": identifier,
                                "error": {"code": -32601, "message": "Unsupported client method"}})
            elif message.get("method") in ("notifications/message", "notifications/progress"):
                pass
        print("[MCP] Studio subprocess closed its output.")

    def _send(self, message: dict) -> None:
        if not self.process or not self.process.stdin or self.process.poll() is not None:
            raise MCPError("Studio MCP subprocess has stopped")
        payload = json.dumps(message, separators=(",", ":"), ensure_ascii=False)
        if len(payload) > MAX_OUTPUT:
            raise MCPError("Request exceeds bridge size cap")
        with self.lock:
            self.process.stdin.write(payload + "\n")
            self.process.stdin.flush()

    def request(self, method: str, params: dict, timeout: int = 120) -> dict:
        response_queue: queue.Queue = queue.Queue(maxsize=1)
        with self.lock:
            self.next_id += 1
            identifier = self.next_id
            self.pending[identifier] = response_queue
        try:
            self._send({"jsonrpc": "2.0", "id": identifier,
                        "method": method, "params": params})
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if self.process and self.process.poll() is not None:
                    raise MCPError(f"Studio MCP subprocess exited with {self.process.returncode}")
                try:
                    return response_queue.get(timeout=min(2, max(0.01, deadline - time.monotonic())))
                except queue.Empty:
                    continue
            raise MCPError(f"Studio MCP {method} timed out after {timeout}s")
        finally:
            with self.lock:
                self.pending.pop(identifier, None)

    def notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def close(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()


def post_json(path: str, payload: dict, timeout: int = 24) -> dict:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_OUTPUT:
        raise MCPError("Studio response too large to forward; nothing sent")
    req = urllib.request.Request(
        RELAY_URL + path, data=body, method="POST",
        headers={"Authorization": "Bearer " + ACCESS_TOKEN,
                 "Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "ArenaStudioMCP-UserClient/1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as reply:
            return json.load(reply)
    except urllib.error.HTTPError as exc:
        if exc.code == 530:
            raise MCPError("Relay tunnel unavailable (HTTP 530); ask the agent for a current URL") from exc
        raise MCPError(f"Relay returned HTTP {exc.code}: {exc.read(240)!r}") from exc
    except urllib.error.URLError as exc:
        raise MCPError(f"Cannot reach relay over HTTPS: {exc}") from exc


def register_with_retries(hello: dict) -> None:
    """A remote tunnel may briefly be unavailable during startup.

    Keep the *already-connected Studio MCP subprocess* alive and wait for
    the relay instead of aborting the whole bridge after a single failure.
    """
    for attempt in range(1, 13):
        try:
            post_json("/worker/hello", hello)
            return
        except (MCPError, TimeoutError) as exc:
            if attempt >= 12:
                raise MCPError(
                    "Cannot register with relay after 12 attempts. "
                    "The tunnel may have expired; ask the agent for a new URL."
                ) from exc
            delay = min(10, attempt * 2)
            print(f"[bridge] Relay not ready ({exc}). Retry {attempt}/12 in {delay}s...")
            time.sleep(delay)


def local_approval(tool: str, arguments: dict) -> bool:
    text = json.dumps(arguments, ensure_ascii=False, indent=2)
    print("\n" + "=" * 60)
    print("STUDIO'YU DEGISTIREBILECEK ISTEK / STUDIO ACTION REQUIRES APPROVAL")
    print("Tool:", tool)
    print("Arguments (first 1200 characters):\n" + text[:1200])
    review_path = None
    if len(text) > 1200:
        # Long edits must be REVIEWABLE before approval, not just a teaser.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                suffix=".json", prefix="arena_studio_review_",
                delete=False) as temp:
            temp.write(text)
            review_path = Path(temp.name)
        print(f"... ({len(text)} characters total). COMPLETE arguments for review:")
        print(review_path)
        print("Open that file BEFORE typing YES. It is deleted after this prompt.")
    print("If you did not request this action or are unsure, press Enter to DENY.")
    try:
        # A separate affirmative answer is required for EACH non-read-only call.
        answer = input("Allow this ONE Studio action? Type YES / Bu TEK isleme izin? YES yaz: ").strip()
    finally:
        if review_path:
            review_path.unlink(missing_ok=True)
    print("=" * 60)
    return answer == "YES"


def main() -> None:
    if platform.system() != "Windows":
        raise MCPError("Run this user-side script on the Windows PC that has Roblox Studio")
    local_app = os.environ.get("LOCALAPPDATA")
    if not local_app:
        raise MCPError("Windows LOCALAPPDATA variable is missing")
    studio_dir = Path(local_app) / "Roblox"
    batch = studio_dir / "mcp.bat"
    if not batch.is_file():
        raise MCPError(f"Studio MCP launcher not found: {batch}. Update Studio and enable its MCP server.")
    if not RELAY_URL.startswith("https://") or len(ACCESS_TOKEN) < 32:
        raise MCPError("Bridge configuration is incomplete")
    print("[bridge] Windows Studio launcher:", batch)
    print("[bridge] Outbound-only HTTPS relay:", RELAY_URL)
    print("[bridge] READ operations permitted; Play, writes and Luau require local YES each time.")
    print("[bridge] Do NOT run this while you have a sensitive or unpublished place open.")
    print("[bridge] Press Ctrl+C to disconnect.\n")
    studio = StdioMCPClient(["cmd.exe", "/d", "/c", ".\\mcp.bat"], cwd=studio_dir)
    try:
        studio.start()
        safe = [tool for tool in studio.tools if tool.get("name") in ALLOWED_TOOLS]
        hello = {"client": "Windows user-operated client", "tools": safe}
        register_with_retries(hello)
        print(f"[bridge] Online; {len(safe)} permitted tool definitions shared with relay.")
        print("[bridge] Wait for requests, or press Ctrl+C to stop.\n")
        network_errors = 0
        while True:
            if studio.process and studio.process.poll() is not None:
                raise MCPError("Studio MCP closed. Check that Studio is open and its MCP switch is enabled.")
            try:
                data = post_json("/worker/poll", {}, timeout=24)
                network_errors = 0
            except (MCPError, TimeoutError) as exc:
                network_errors += 1
                print("[bridge] Relay unavailable:", exc)
                if network_errors > 8:
                    raise MCPError("Relay has been unavailable repeatedly; stopping safely") from exc
                time.sleep(min(15, network_errors * 2))
                continue
            if data.get("needs_hello"):
                # If the agent's relay restarted, register tool definitions
                # again rather than silently appearing connected but unusable.
                register_with_retries(hello)
                continue
            job = data.get("job")
            if not job:
                continue
            identifier = job.get("id")
            tool = job.get("tool")
            arguments = job.get("arguments")
            if not (isinstance(identifier, str) and isinstance(tool, str)
                    and isinstance(arguments, dict)):
                print("[bridge] Ignoring malformed relay request")
                continue
            try:
                if tool not in ALLOWED_TOOLS:
                    raise MCPError("Requested tool is not allowed by local client")
                if tool in APPROVAL_TOOLS and not local_approval(tool, arguments):
                    raise MCPError("User denied this Studio action")
                print("[bridge] Invoking Studio:", tool)
                response = studio.request("tools/call",
                                          {"name": tool, "arguments": arguments},
                                          timeout=180)
                result = {"id": identifier, "ok": "error" not in response,
                          "response": response}
            except (MCPError, ValueError, OSError) as exc:
                result = {"id": identifier, "ok": False, "response": {"error": str(exc)}}
            try:
                report = post_json("/worker/result", result, timeout=50)
                print("[bridge] Result sent:", tool,
                      "; images:", len(report.get("images", [])))
            except (MCPError, TimeoutError) as exc:
                # Never retry a possibly mutating Studio command. We don't
                # know whether the relay accepted the result before failure.
                print("[bridge] Could not return the result:", exc)
    finally:
        studio.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bridge] Disconnected on user request.")
    except (MCPError, OSError, RuntimeError) as error:
        print("\n[bridge] ERROR:", error)
        sys.exit(1)
