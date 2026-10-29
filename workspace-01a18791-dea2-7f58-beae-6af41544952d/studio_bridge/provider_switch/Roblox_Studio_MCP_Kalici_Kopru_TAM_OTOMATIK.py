#!/usr/bin/env python3
"""Windows Studio MCP client (TAM OTOMATIK + OYUNCU SESLI ALARM & BILDIRIM):
encrypted ntfy.envs.net mailbox.

User-requested full auto-approval edition + non-intrusive gamer alert system:
- ALL 15 Studio MCP tools in ALLOWED_TOOLS execute without blocking on console YES prompts.
- Adds built-in local tool `notify_user` so Arena Agent can ring an audible
  multi-tone WAV alarm (through default Windows headphones/speakers via winsound)
  AND show a non-focus-stealing Windows tray/balloon notification whenever work
  finishes or a question/approval is waiting — without minimizing fullscreen games!
- No publish tool is included. Ctrl+C stops.
Keep alongside Roblox_Studio_Bus.py and Roblox_Studio_MCP_Gizli_Ayar.json.
"""
from __future__ import annotations

import base64
import io
import json
import math
import os
import platform
import queue
import secrets
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave
from pathlib import Path

from Roblox_Studio_Bus import BusError, EncryptedBus

READ_TOOLS = frozenset({
    "list_roblox_studios", "get_studio_state", "search_game_tree",
    "inspect_instance", "script_search", "script_grep", "script_read",
    "get_console_output", "screen_capture", "notify_user",
})
APPROVAL_TOOLS = frozenset({
    "start_stop_play", "execute_luau", "multi_edit", "character_navigation",
    "user_mouse_input", "user_keyboard_input",
})
ALLOWED_TOOLS = READ_TOOLS | APPROVAL_TOOLS
MAX_TOOL_REQUEST = 14_000_000

NOTIFY_TOOL_SCHEMA = {
    "name": "notify_user",
    "title": "Notify User (Audio Alarm + Windows Toast)",
    "description": (
        "Plays an audible chime/alarm through the user's Windows headphones/speakers "
        "and displays a non-focus-stealing Windows tray balloon notification so the "
        "user knows while gaming that work is finished or a question awaits."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short notification title (Turkish).",
            },
            "message": {
                "type": "string",
                "description": "Notification message body (Turkish).",
            },
            "mode": {
                "type": "string",
                "enum": ["done", "question", "review", "test"],
                "description": "Alert melody style.",
            },
            "repeat": {
                "type": "integer",
                "description": "How many times to play the chime sequence (1-4, default 2).",
            },
        },
        "required": ["message"],
    },
    "annotations": {
        "title": "Notify User",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}


def build_chime_wav(notes_hz: list[tuple[float, float]], volume: float = 0.55) -> bytes:
    """Synthesize a crisp 44.1 kHz 16-bit mono WAV chime in memory (zero external files)."""
    sample_rate = 44100
    pcm = bytearray()
    for freq, dur in notes_hz:
        n_samples = max(1, int(sample_rate * dur))
        if freq <= 0.0:
            pcm.extend(b"\x00\x00" * n_samples)
            continue
        attack = max(1, int(sample_rate * 0.012))
        release = max(1, int(sample_rate * min(0.06, dur * 0.35)))
        for i in range(n_samples):
            t = i / sample_rate
            if i < attack:
                env = i / attack
            elif i > n_samples - release:
                env = max(0.0, (n_samples - i) / release)
            else:
                env = math.exp(-2.2 * (t / max(dur, 0.05)))
            # Fundamental + warm octave/fifth harmonics so it cuts cleanly through game audio
            val = (
                0.70 * math.sin(2.0 * math.pi * freq * t)
                + 0.22 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                + 0.08 * math.sin(2.0 * math.pi * (freq * 1.5) * t)
            )
            sample = int(max(-32767, min(32767, val * env * volume * 32767)))
            pcm.extend(struct.pack("<h", sample))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(pcm))
    return buf.getvalue()


MELODIES: dict[str, list[tuple[float, float]]] = {
    "test": [
        (659.25, 0.11), (0.0, 0.03), (880.0, 0.18),
    ],
    "done": [
        (587.33, 0.13), (783.99, 0.13), (987.77, 0.15), (1174.66, 0.34),
        (0.0, 0.22),
        (587.33, 0.13), (783.99, 0.13), (987.77, 0.15), (1174.66, 0.40),
    ],
    "question": [
        (659.25, 0.14), (880.00, 0.14), (1046.50, 0.28),
        (0.0, 0.18),
        (659.25, 0.14), (880.00, 0.14), (1318.51, 0.38),
    ],
    "review": [
        (523.25, 0.12), (659.25, 0.12), (783.99, 0.12), (1046.50, 0.36),
        (0.0, 0.22),
        (523.25, 0.12), (659.25, 0.12), (783.99, 0.12), (1046.50, 0.42),
    ],
}


def _show_windows_balloon_nonblocking(title: str, message: str) -> None:
    """Display a Windows system tray balloon tip WITHOUT stealing fullscreen game focus."""
    if sys.platform != "win32":
        return
    safe_title = title.replace("'", " ").replace('"', " ")[:60]
    safe_msg = message.replace("'", " ").replace('"', " ")[:220]
    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$n = New-Object System.Windows.Forms.NotifyIcon; "
        "$n.Icon = [System.Drawing.SystemIcons]::Information; "
        "$n.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info; "
        f"$n.BalloonTipTitle = '{safe_title}'; "
        f"$n.BalloonTipText = '{safe_msg}'; "
        "$n.Visible = $true; "
        "$n.ShowBalloonTip(9000); "
        "Start-Sleep -Milliseconds 9500; "
        "$n.Dispose();"
    )
    encoded = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
    try:
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-WindowStyle", "Hidden",
                "-EncodedCommand", encoded,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except OSError:
        pass


def trigger_gamer_alert(title: str, message: str, mode: str = "done", repeat: int = 2) -> None:
    """Play WAV alarm on default audio output + non-intrusive tray notification in background."""
    notes = MELODIES.get(mode, MELODIES["done"])
    reps = max(1, min(int(repeat), 4))
    full_seq: list[tuple[float, float]] = []
    for idx in range(reps):
        if idx > 0:
            full_seq.append((0.0, 0.32))
        full_seq.extend(notes)
    wav_data = build_chime_wav(full_seq, volume=0.62)

    print("\n" + "*" * 66)
    print(f"  [ARENA BILDIRIM / {mode.upper()}] {title}")
    print(f"  {message}")
    print("*" * 66 + "\n")

    def _audio_worker() -> None:
        if sys.platform == "win32":
            try:
                import winsound
                winsound.PlaySound(wav_data, winsound.SND_MEMORY)
                return
            except Exception:
                try:
                    import winsound
                    for _ in range(reps):
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                        time.sleep(0.45)
                    return
                except Exception:
                    pass
        sys.stdout.write("\a")
        sys.stdout.flush()

    threading.Thread(target=_audio_worker, daemon=True).start()
    if mode != "test":
        _show_windows_balloon_nonblocking(title, message)


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
                               "version": "1.2.0"},
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
    advertised["notify_user"] = NOTIFY_TOOL_SCHEMA
    hello = {"kind": "HELLO", "session": session,
             "auto_policy": "FULL_AUTO_ALL_TOOLS_V2_ALARM",
             "tools": list(advertised.values()), "time": time.time()}
    announce_with_retries(bus, hello)
    print(f"[bridge] ONLINE via encrypted HTTPS mailbox; {len(advertised)} supported tools (notify_user DAHIL).")
    print("[bridge] OYUNCU SESLI ALARM + WINDOWS BILDIRIM SISTEMI AKTIF!")
    print("[bridge] Oyundayken islem bittiginde veya soru soruldugunda kulakliktan melodi calar (oyunu alta almaz).")
    trigger_gamer_alert(
        "Köprü Hazır",
        "Sesli alarm testi başarılı! Artık oyuna geçebilirsiniz.",
        mode="test",
        repeat=1,
    )
    cursor = "all"
    processed: set[str] = set()
    network_errors = 0
    next_hello = time.monotonic() + 240
    while True:
        if studio.process and studio.process.poll() is not None:
            raise MCPError("Studio MCP stopped. Check whether Studio is still open.")
        if time.monotonic() >= next_hello:
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
                if tool == "notify_user":
                    t_str = str(arguments.get("title") or "Arena Bildirimi")
                    m_str = str(arguments.get("message") or "Çalışma tamamlandı, onayınız bekleniyor.")
                    mode_str = str(arguments.get("mode") or "done")
                    rep_int = int(arguments.get("repeat") or 2)
                    trigger_gamer_alert(t_str, m_str, mode=mode_str, repeat=rep_int)
                    output = {
                        "result": {
                            "isError": False,
                            "content": [{"type": "text", "text": f"ALARM_PLAYED:{mode_str}:{t_str}"}],
                        }
                    }
                else:
                    if tool in APPROVAL_TOOLS:
                        target = arguments.get("file_path") or arguments.get("path") or arguments.get("studio_id") or ""
                        print(f"[tam-otomatik] AUTO-ALLOW {tool} ({target})")
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
    print("[bridge] TAM OTOMATIK MOD + OYUNCU SESLI ALARM SISTEMI (V2) AKTIF!")
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
