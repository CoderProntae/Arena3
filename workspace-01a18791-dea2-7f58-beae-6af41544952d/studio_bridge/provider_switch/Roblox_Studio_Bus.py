#!/usr/bin/env python3
"""Encrypted, outbound-HTTPS-only mailbox for Roblox Studio MCP.

Both endpoints make ordinary HTTPS requests to ntfy.envs.net. No public tunnel, inbound port, Roblox credentials, or always-on
agent-side process is required. Provider may have its own usage limits. This third-party host receives only
Fernet-authenticated encrypted payloads; topics and key are session secrets.
This is an optional third-party transport, NOT an official Arena connector.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError as exc:
    raise SystemExit(
        "Missing encryption library. Install once: python -m pip install cryptography"
    ) from exc

MARKER = "ArenaStudioEncryptedV1"
FRAGMENT_MARKER = "ArenaStudioChunkV1"
MAX_ATTACHMENT = 1_750_000  # below ntfy.envs.net's documented public 2 MB/file limit
MAX_RAW_BYTES = 14_000_000
USER_AGENT = "ArenaRobloxStudioEncryptedBridge/1"


class BusError(RuntimeError):
    pass


class EncryptedBus:
    def __init__(self, config: dict):
        self.url = str(config.get("base_url", "https://ntfy.envs.net")).rstrip("/")
        if self.url != "https://ntfy.envs.net":
            raise BusError("Only the explicitly selected community host https://ntfy.envs.net is allowed")
        self.commands = str(config["commands"])
        self.responses = str(config["responses"])
        for topic in (self.commands, self.responses):
            if not topic.startswith("arena_studio_") or len(topic) > 64:
                raise BusError("Invalid random session topic")
            if not all(c.isalnum() or c in "-_" for c in topic):
                raise BusError("Invalid topic characters")
        self.cipher = Fernet(str(config["fernet_key"]).encode("ascii"))

    @staticmethod
    def from_file(path: str | Path) -> "EncryptedBus":
        return EncryptedBus(json.loads(Path(path).read_text(encoding="utf-8")))

    @staticmethod
    def _http(req: urllib.request.Request, timeout: int = 25) -> bytes:
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read(MAX_RAW_BYTES + 1)
                if len(content) > MAX_RAW_BYTES:
                    raise BusError("HTTP response exceeds safe size cap")
                return content
        except urllib.error.HTTPError as exc:
            raise BusError(f"Community ntfy HTTPS {exc.code}: {exc.read(220)!r}") from exc
        except urllib.error.URLError as exc:
            raise BusError(f"Community ntfy HTTPS unavailable: {exc}") from exc

    def _post(self, topic: str, data: bytes, title: str,
              filename: str | None = None) -> dict:
        if len(data) > MAX_ATTACHMENT:
            raise BusError("One attachment is too large")
        headers = {"User-Agent": USER_AGENT, "X-Title": title,
                   "X-Priority": "1"}
        if filename:
            headers["X-Filename"] = filename
            headers["Content-Type"] = "application/octet-stream"
        else:
            headers["Content-Type"] = "text/plain; charset=utf-8"
        raw = self._http(urllib.request.Request(
            f"{self.url}/{topic}", data=data, method="POST", headers=headers),
            timeout=40)
        event = json.loads(raw)
        if not isinstance(event, dict) or not isinstance(event.get("id"), str):
            raise BusError("Community publish did not return a message ID")
        if filename and not isinstance(event.get("attachment"), dict):
            raise BusError("Community host did not store the attachment")
        return event

    def _pack(self, obj: dict) -> bytes:
        plaintext = json.dumps(obj, ensure_ascii=False,
                               separators=(",", ":")).encode("utf-8")
        if len(plaintext) > MAX_RAW_BYTES:
            raise BusError("MCP response exceeds 14 MB safety cap")
        return self.cipher.encrypt(zlib.compress(plaintext, 9))

    def _unpack(self, token: bytes) -> dict | None:
        try:
            packed = self.cipher.decrypt(token)
            # Limit DECOMPRESSED size too, not just the encrypted input.
            unzip = zlib.decompressobj()
            plaintext = unzip.decompress(packed, MAX_RAW_BYTES + 1)
            if len(plaintext) > MAX_RAW_BYTES or not unzip.eof:
                raise BusError("Decompressed message exceeds safety cap")
            obj = json.loads(plaintext)
            return obj if isinstance(obj, dict) else None
        except (InvalidToken, ValueError, UnicodeDecodeError,
                zlib.error, json.JSONDecodeError):
            return None

    def _download(self, url: str) -> bytes:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "ntfy.envs.net" or \
                not parsed.path.startswith("/file/"):
            raise BusError("Refusing an attachment URL outside ntfy.envs.net/file/")
        return self._http(urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT}), timeout=45)

    def publish(self, topic: str, obj: dict) -> str:
        if topic not in (self.commands, self.responses):
            raise BusError("Unknown session topic")
        token = self._pack(obj)
        if len(token) <= 3500:
            return self._post(topic, token, MARKER)["id"]
        if len(token) <= MAX_ATTACHMENT:
            name = "studio-encrypted-" + secrets.token_hex(8) + ".bin"
            return self._post(topic, token, MARKER, name)["id"]
        # Screenshot or huge tool result: upload independently encrypted
        # chunks and then an ENCRYPTED manifest containing their URLs and
        # hashes. No fragment is acted upon until the manifest authenticates.
        chunks = []
        tx = secrets.token_hex(12)
        for i in range(0, len(token), MAX_ATTACHMENT):
            fragment = token[i:i + MAX_ATTACHMENT]
            event = self._post(topic, fragment, FRAGMENT_MARKER,
                               f"studio-{tx}-{i // MAX_ATTACHMENT}.bin")
            chunks.append({"url": event["attachment"]["url"],
                           "sha256": hashlib.sha256(fragment).hexdigest()})
        manifest = {"kind": "FRAGMENTS", "tx": tx,
                    "length": len(token), "chunks": chunks}
        return self._post(topic, self._pack(manifest), MARKER)["id"]

    def read(self, topic: str, since: str = "all") -> tuple[list[dict], str]:
        if topic not in (self.commands, self.responses):
            raise BusError("Unknown session topic")
        query = urllib.parse.urlencode({"poll": "1", "since": since})
        data = self._http(urllib.request.Request(
            f"{self.url}/{topic}/json?{query}",
            headers={"User-Agent": USER_AGENT}), timeout=25)
        events = []
        cursor = since
        for line in data.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict) or event.get("event") != "message":
                continue
            identifier = event.get("id")
            if not isinstance(identifier, str):
                continue
            cursor = identifier
            if event.get("title") != MARKER:
                continue
            try:
                attachment = event.get("attachment")
                if isinstance(attachment, dict):
                    token = self._download(str(attachment.get("url", "")))
                else:
                    token = str(event.get("message", "")).encode("ascii")
                obj = self._unpack(token)
                if obj and obj.get("kind") == "FRAGMENTS":
                    pieces = []
                    items = obj.get("chunks")
                    if not isinstance(items, list) or len(items) > 9:
                        continue
                    for part in items:
                        chunk = self._download(str(part.get("url", "")))
                        if hashlib.sha256(chunk).hexdigest() != part.get("sha256"):
                            raise BusError("Attachment SHA-256 mismatch")
                        pieces.append(chunk)
                    joined = b"".join(pieces)
                    if len(joined) != obj.get("length"):
                        raise BusError("Attachment length mismatch")
                    obj = self._unpack(joined)
                if isinstance(obj, dict):
                    obj["_ntfy_id"] = identifier
                    obj["_ntfy_time"] = event.get("time")
                    events.append(obj)
            except (BusError, UnicodeEncodeError, AttributeError):
                # Never execute unauthenticated, oversized or malformed data.
                continue
        return events, cursor
