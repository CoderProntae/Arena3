#!/usr/bin/env python3
"""Live Workspace & Render Gallery Server for Arena Sandbox Preview.

Binds to 0.0.0.0:8080, accepts any Host/Origin, permits iframe embedding, uses
strictly relative URLs, and streams real-time updates of all images, 3D GLBs,
test captures, and formatted Markdown (.md) / code files in /home/user.
"""
from __future__ import annotations
import html
import json
import mimetypes
import os
import posixpath
import re
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path("/home/user").resolve()
PORT = int(os.environ.get("GALLERY_PORT", "8080"))
# This preview is public to its link: never expose bridge settings or workspace secrets.
PUBLIC_DIRS = {"reports", "model_exports"}
PUBLIC_IMAGE_DIR = "studio_bridge/provider_switch/community_results"
PUBLIC_FILES = {
    "AEGIS_REAKTOR_ANA_YOL_HARITASI_VE_MODELLEME_PLANI.md",
    "faz4/glass_laser/M14_GELISTIRME_VE_TEST.md",
    "faz4/pipe_damage/FAZ42_43_TEST_RAPORU.md",
    "audit_karsilastirma/MELTDOWN_LAZER_CAM_NOTU.md",
    "audit_karsilastirma/STUDIO_EDIT_MESH_ONARIMI.md",
}

HIDDEN_NAMES = {
    "Roblox_Studio_MCP_Gizli_Ayar.json",
    ".git",
    ".netrc",
    ".git-credentials",
}
SKIP_WALK_DIRS = {
    "studio_pydeps",
    "modeldeps",
    "modelrender",
    "archived_history",
    "community_results_archive",
    "__pycache__",
    "node_modules",
    ".venv",
}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
TEXT_EXTS = {".md", ".txt", ".lua", ".luau", ".py", ".json", ".html", ".csv"}
MODEL_EXTS = {".glb", ".gltf", ".zip", ".rbxlx"}


def is_safe_subpath(rel: str) -> Path | None:
    clean = posixpath.normpath("/" + rel.lstrip("/")).lstrip("/")
    if not clean or (clean.split("/")[0] not in PUBLIC_DIRS and clean not in PUBLIC_FILES and not (clean.startswith(PUBLIC_IMAGE_DIR + "/") and Path(clean).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})):
        return None
    target = (ROOT / clean).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    for part in target.parts:
        if part in HIDDEN_NAMES:
            return None
    if target.name in HIDDEN_NAMES:
        return None
    return target


def scan_workspace() -> dict:
    now = time.time()
    images = []
    models = []
    docs = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = Path(dirpath).resolve().relative_to(ROOT)
        filtered = []
        for d in dirnames:
            candidate = (rel_dir / d).as_posix()
            if d not in PUBLIC_DIRS and not (rel_dir.parts and rel_dir.parts[0] in PUBLIC_DIRS) and not any(x.startswith(candidate + "/") for x in PUBLIC_FILES) and not (PUBLIC_IMAGE_DIR == candidate or PUBLIC_IMAGE_DIR.startswith(candidate + "/")):
                continue
            if d in HIDDEN_NAMES or d in SKIP_WALK_DIRS:
                continue
            if d == ".cache":
                filtered.append(d)
                continue
            if rel_dir.parts and rel_dir.parts[0] == ".cache" and d not in {"model_debug", "side_walls_rev02_candidate"}:
                continue
            filtered.append(d)
        dirnames[:] = sorted(filtered)

        for fn in filenames:
            candidate = (rel_dir / fn).as_posix()
            if not (rel_dir.parts and rel_dir.parts[0] in PUBLIC_DIRS) and candidate not in PUBLIC_FILES and not (candidate.startswith(PUBLIC_IMAGE_DIR + "/") and Path(candidate).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}):
                continue
            if fn in HIDDEN_NAMES or fn.startswith("."):
                continue
            fpath = Path(dirpath) / fn
            try:
                st = fpath.stat()
            except OSError:
                continue
            rel_str = fpath.resolve().relative_to(ROOT).as_posix()
            ext = fpath.suffix.lower()
            item = {
                "path": rel_str,
                "name": fn,
                "folder": str(rel_dir).replace("\\", "/") if str(rel_dir) != "." else "/",
                "size": st.st_size,
                "mtime": round(st.st_mtime, 2),
                "age_sec": max(0, int(now - st.st_mtime)),
                "ext": ext,
            }
            if ext in IMAGE_EXTS:
                images.append(item)
            elif ext in MODEL_EXTS:
                models.append(item)
            elif ext in TEXT_EXTS:
                docs.append(item)

    images.sort(key=lambda x: x["mtime"], reverse=True)
    models.sort(key=lambda x: x["mtime"], reverse=True)
    docs.sort(key=lambda x: (0 if x["ext"] == ".md" else 1, -x["mtime"]))
    return {
        "server_time": now,
        "images": images[:120],
        "models": models[:60],
        "docs": docs[:80],
    }


# ============================================================================
# SELF-CONTAINED GITHUB-FLAVORED MARKDOWN -> HTML RENDERER (ZERO EXTERNAL CDN)
# ============================================================================
MD_CSS = r"""
  .md-view {
    width: 100%; max-width: 1120px; margin: 0 auto;
    background: #111827; border: 1px solid #2a3a56; border-radius: 12px;
    padding: 28px 36px; color: #e5edf8; font-size: 15px; line-height: 1.68;
    box-shadow: 0 12px 32px rgba(0,0,0,0.45);
  }
  .md-view h1, .md-view h2, .md-view h3, .md-view h4, .md-view h5, .md-view h6 {
    color: #f8fafc; margin-top: 1.5em; margin-bottom: 0.55em; line-height: 1.3; font-weight: 700;
  }
  .md-view h1:first-child, .md-view h2:first-child { margin-top: 0; }
  .md-view h1 { font-size: 1.85em; padding-bottom: 0.32em; border-bottom: 1px solid #2a3a56; color: #7dd3fc; }
  .md-view h2 { font-size: 1.42em; padding-bottom: 0.26em; border-bottom: 1px solid #1f2d44; color: #bae6fd; }
  .md-view h3 { font-size: 1.18em; color: #e2e8f0; }
  .md-view p { margin: 0.7em 0; }
  .md-view hr { border: 0; border-top: 1px solid #2a3a56; margin: 1.6em 0; }
  .md-view a { color: #38bdf8; text-decoration: none; font-weight: 600; }
  .md-view a:hover { text-decoration: underline; }
  .md-view code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    background: #1e293b; color: #93c5fd; padding: 2px 6px; border-radius: 5px;
    border: 1px solid #334155; font-size: 0.88em;
  }
  .md-view pre {
    background: #090d16; border: 1px solid #283548; border-radius: 8px;
    padding: 14px 16px; overflow-x: auto; margin: 1em 0;
  }
  .md-view pre code {
    background: transparent; border: 0; padding: 0; color: #e2e8f0; font-size: 13px; line-height: 1.52;
  }
  .md-view blockquote {
    margin: 1em 0; padding: 8px 16px; border-left: 4px solid #38bdf8;
    background: rgba(56, 189, 248, 0.08); border-radius: 0 8px 8px 0; color: #cbd5e1;
  }
  .md-view ul, .md-view ol { padding-left: 1.6em; margin: 0.6em 0; }
  .md-view li { margin: 0.32em 0; }
  .md-view li.task-item { list-style: none; margin-left: -1.35em; display: flex; align-items: flex-start; gap: 9px; }
  .md-view .chk {
    display: inline-flex; align-items: center; justify-content: center;
    width: 18px; height: 18px; border-radius: 4px; font-size: 12px; font-weight: 800;
    margin-top: 3px; flex-shrink: 0;
  }
  .md-view .chk.done { background: rgba(16, 185, 129, 0.22); border: 1px solid #34d399; color: #6ee7b7; }
  .md-view .chk.todo { background: rgba(148, 163, 184, 0.12); border: 1px solid #64748b; color: transparent; }
  .md-view .table-wrap { overflow-x: auto; margin: 1.1em 0; }
  .md-view table {
    width: 100%; border-collapse: collapse; background: #0d1422;
    border: 1px solid #2a3a56; border-radius: 8px; overflow: hidden; font-size: 13.8px;
  }
  .md-view th, .md-view td {
    padding: 9px 13px; border: 1px solid #24324a; text-align: left; vertical-align: top;
  }
  .md-view th { background: #182338; color: #bae6fd; font-weight: 700; }
  .md-view tr:nth-child(even) td { background: rgba(25, 35, 54, 0.42); }
  .md-view tr:hover td { background: rgba(56, 189, 248, 0.08); }
  .md-view img { max-width: 100%; border-radius: 8px; border: 1px solid #2a3a56; margin: 8px 0; }
"""


def _render_inline_md(text: str) -> str:
    code_Tokens: list[str] = []

    def _stash_code(m: re.Match) -> str:
        idx = len(code_Tokens)
        code_Tokens.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00CODE{idx}\x00"

    s = re.sub(r"`([^`]+)`", _stash_code, text)
    s = html.escape(s)

    # Images ![alt](url)
    s = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">',
        s,
    )
    # Links [label](url)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        s,
    )
    # Bold + Italic
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)

    for idx, tok in enumerate(code_Tokens):
        s = s.replace(f"\x00CODE{idx}\x00", tok)
    return s


def render_markdown_to_html(md_text: str) -> str:
    lines = md_text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Fenced code block ```
        m_fence = re.match(r"^```(\w*)\s*$", stripped)
        if m_fence:
            lang = html.escape(m_fence.group(1))
            i += 1
            code_lines = []
            while i < n and not re.match(r"^```\s*$", lines[i].strip()):
                code_lines.append(html.escape(lines[i]))
                i += 1
            i += 1
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>" + "\n".join(code_lines) + "</code></pre>")
            continue

        # Horizontal rule
        if re.match(r"^(---|\*\*\*|___)\s*$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Heading # .. ######
        m_h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_h:
            lvl = len(m_h.group(1))
            out.append(f"<h{lvl}>{_render_inline_md(m_h.group(2).strip())}</h{lvl}>")
            i += 1
            continue

        # GFM Table: header row with | followed by separator row |---|
        if "|" in stripped and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|[\s:\-|]*$", lines[i + 1].strip()) and "-" in lines[i + 1]:
            def _split_row(r: str) -> list[str]:
                r = r.strip()
                if r.startswith("|"):
                    r = r[1:]
                if r.endswith("|"):
                    r = r[:-1]
                return [c.strip() for c in r.split("|")]

            headers = _split_row(line)
            i += 2  # skip header + separator
            t_rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                t_rows.append(_split_row(lines[i]))
                i += 1
            th_html = "".join(f"<th>{_render_inline_md(h)}</th>" for h in headers)
            tr_html = []
            for r in t_rows:
                cells = [r[idx] if idx < len(r) else "" for idx in range(len(headers))]
                tr_html.append("<tr>" + "".join(f"<td>{_render_inline_md(c)}</td>" for c in cells) + "</tr>")
            out.append(f'<div class="table-wrap"><table><thead><tr>{th_html}</tr></thead><tbody>{"".join(tr_html)}</tbody></table></div>')
            continue

        # Blockquote >
        if stripped.startswith(">"):
            bq_lines = []
            while i < n and lines[i].strip().startswith(">"):
                bq_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(_render_inline_md(x) for x in bq_lines) + "</blockquote>")
            continue

        # Lists (unordered -, *, + or ordered 1.) including nested indented items & checkboxes
        m_li = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m_li:
            list_items: list[tuple[int, bool, str]] = []
            while i < n:
                ml = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if not ml:
                    break
                indent = len(ml.group(1).replace("\t", "  "))
                is_ord = ml.group(2).endswith(".")
                list_items.append((indent, is_ord, ml.group(3)))
                i += 1

            # Build flat/2-level clean HTML list
            tag0 = "ol" if list_items[0][1] else "ul"
            buf = [f"<{tag0}>"]
            sub_open = False
            base_indent = list_items[0][0]
            for indent, is_ord, content in list_items:
                if indent > base_indent + 1 and not sub_open:
                    buf.append("<ul>")
                    sub_open = True
                elif indent <= base_indent + 1 and sub_open:
                    buf.append("</ul>")
                    sub_open = False

                m_chk = re.match(r"^\[([ xX])\]\s+(.*)$", content)
                if m_chk:
                    checked = m_chk.group(1).lower() == "x"
                    mark = "✓" if checked else ""
                    cls = "done" if checked else "todo"
                    buf.append(
                        f'<li class="task-item"><span class="chk {cls}">{mark}</span>'
                        f'<span>{_render_inline_md(m_chk.group(2))}</span></li>'
                    )
                else:
                    buf.append(f"<li>{_render_inline_md(content)}</li>")
            if sub_open:
                buf.append("</ul>")
            buf.append(f"</{tag0}>")
            out.append("".join(buf))
            continue

        # Paragraph
        para = []
        while i < n:
            cur = lines[i].strip()
            if (
                not cur
                or cur.startswith("```")
                or cur.startswith("#")
                or cur.startswith(">")
                or re.match(r"^(---|\*\*\*|___)\s*$", cur)
                or re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i])
                or ("|" in cur and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|[\s:\-|]*$", lines[i + 1].strip()) and "-" in lines[i + 1])
            ):
                break
            para.append(_render_inline_md(cur))
            i += 1
        out.append("<p>" + " ".join(para) + "</p>")

    return "\n".join(out)


def build_standalone_md_page(rel_path: str, md_text: str) -> bytes:
    rendered = render_markdown_to_html(md_text)
    rel_q = urllib.parse.quote(rel_path)
    base_depth = rel_path.count("/") + 1
    root_back = "../" * base_depth
    page = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(Path(rel_path).name)} — AEGIS Markdown Görünümü</title>
<style>
  body {{
    margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    background: #0b0f17; color: #e5edf8; padding-bottom: 60px;
  }}
  .topbar {{
    position: sticky; top: 0; z-index: 20;
    background: rgba(11, 15, 23, 0.95); backdrop-filter: blur(8px);
    border-bottom: 1px solid #2a3a56; padding: 12px 24px;
    display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between;
  }}
  .btn {{
    background: #192336; color: #e5edf8; border: 1px solid #2a3a56;
    border-radius: 7px; padding: 7px 13px; font-size: 13px; text-decoration: none; font-weight: 600;
  }}
  .btn:hover {{ border-color: #38bdf8; color: #fff; }}
  .wrap {{ padding: 24px 20px; }}
  {MD_CSS}
</style>
</head>
<body>
  <div class="topbar">
    <div style="display:flex;align-items:center;gap:12px;">
      <a class="btn" href="{root_back}">← Canlı Galeriye Dön</a>
      <strong style="font-size:14px;color:#7dd3fc;">📄 {html.escape(rel_path)}</strong>
    </div>
    <div style="display:flex;gap:8px;">
      <a class="btn" href="{root_back}raw/{rel_q}?raw=1" target="_blank">Ham Metin (.txt)</a>
      <a class="btn" href="{root_back}raw/{rel_q}?download=1" download="{html.escape(Path(rel_path).name)}">İndir (.md)</a>
    </div>
  </div>
  <div class="wrap">
    <article class="md-view">{rendered}</article>
  </div>
</body>
</html>"""
    return page.encode("utf-8")


INDEX_HTML = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AEGIS Reaktörü — Canlı Görsel, Test & 3B Model Merkezi</title>
<style>
  :root {{
    --bg: #0b0f17;
    --panel: #131b29;
    --panel2: #192336;
    --border: #2a3a56;
    --accent: #38bdf8;
    --green: #34d399;
    --amber: #fbbf24;
    --text: #e5edf8;
    --muted: #93a6c4;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    background: var(--bg); color: var(--text);
  }}
  header {{
    position: sticky; top: 0; z-index: 20;
    background: rgba(11, 15, 23, 0.94); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px; display: flex; flex-wrap: wrap; gap: 12px;
    align-items: center; justify-content: space-between;
  }}
  .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 17px; }}
  .dot {{
    width: 10px; height: 10px; border-radius: 50%; background: var(--green);
    box-shadow: 0 0 10px var(--green); animation: pulse 1.6s infinite;
  }}
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
  .controls {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
  button, .tab, input {{
    background: var(--panel2); color: var(--text); border: 1px solid var(--border);
    border-radius: 7px; padding: 7px 12px; font-size: 13px; cursor: pointer;
  }}
  button:hover, .tab:hover {{ border-color: var(--accent); }}
  .tab.active {{ background: #163452; border-color: var(--accent); color: #fff; font-weight: 600; }}
  input {{ cursor: text; min-width: 210px; }}
  main {{ padding: 18px 20px 60px; max-width: 1760px; margin: 0 auto; }}
  .status-bar {{
    font-size: 12px; color: var(--muted); margin-bottom: 14px;
    display: flex; gap: 18px; flex-wrap: wrap;
  }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 14px;
  }}
  .card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    overflow: hidden; display: flex; flex-direction: column;
    transition: transform 0.12s, border-color 0.12s;
  }}
  .card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
  .card.fresh {{ border-color: var(--green); box-shadow: 0 0 0 1px rgba(52,211,153,0.35); }}
  .thumb-wrap {{
    width: 100%; aspect-ratio: 16 / 10; background: #070a10;
    display: flex; align-items: center; justify-content: center; overflow: hidden; cursor: zoom-in;
    position: relative;
  }}
  .thumb-wrap img {{ width: 100%; height: 100%; object-fit: contain; }}
  .badge {{
    position: absolute; top: 8px; left: 8px; padding: 3px 8px; border-radius: 5px;
    font-size: 11px; font-weight: 700; background: rgba(8,14,24,0.85); border: 1px solid var(--border);
  }}
  .badge.new {{ background: rgba(6,78,59,0.92); border-color: var(--green); color: #a7f3d0; }}
  .meta {{ padding: 10px 12px; font-size: 12px; display: flex; flex-direction: column; gap: 4px; }}
  .fname {{ font-weight: 600; color: #fff; word-break: break-all; font-size: 13px; }}
  .fsub {{ color: var(--muted); display: flex; justify-content: space-between; gap: 8px; }}
  .list-table {{
    width: 100%; border-collapse: collapse; background: var(--panel);
    border: 1px solid var(--border); border-radius: 10px; overflow: hidden; font-size: 13px;
  }}
  .list-table th, .list-table td {{
    padding: 9px 12px; border-bottom: 1px solid var(--border); text-align: left;
  }}
  .list-table th {{ background: var(--panel2); color: var(--muted); font-weight: 600; }}
  .list-table tr:hover td {{ background: rgba(56, 189, 248, 0.06); }}
  a.link {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
  a.link:hover {{ text-decoration: underline; }}
  .ext-pill {{
    display: inline-block; padding: 2px 7px; border-radius: 5px; font-size: 11px;
    font-weight: 700; margin-right: 6px; background: #1e293b; color: #93c5fd; border: 1px solid #334155;
  }}
  .ext-pill.md {{ background: rgba(14, 116, 144, 0.28); color: #67e8f9; border-color: #0891b2; }}
  /* Lightbox & Markdown/Text Modal */
  .modal {{
    position: fixed; inset: 0; z-index: 100; background: rgba(4, 7, 13, 0.93);
    display: none; flex-direction: column;
  }}
  .modal.open {{ display: flex; }}
  .modal-top {{
    padding: 10px 18px; background: var(--panel); border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  }}
  .modal-body {{
    flex: 1; overflow: auto; display: flex; align-items: flex-start; justify-content: center; padding: 20px;
  }}
  .modal-body.img-mode {{ align-items: center; }}
  .modal-body img.lightbox-img {{ max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.15s; cursor: zoom-in; }}
  .modal-body img.lightbox-img.zoomed {{ max-width: none; max-height: none; cursor: zoom-out; }}
  pre.doc-view {{
    width: 100%; max-width: 1200px; margin: 0 auto; background: var(--panel);
    border: 1px solid var(--border); border-radius: 8px; padding: 18px;
    color: var(--text); white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.5;
  }}
  {MD_CSS}
</style>
</head>
<body>
<header>
  <div class="brand">
    <span class="dot" id="liveDot"></span>
    <span>AEGIS Reaktörü — Canlı Çalışma Ortamı & Görsel Galerisi</span>
  </div>
  <div class="controls">
    <a href="/raw/reports/AEGIS_GUNCEL_PLAN_VE_FIKIRLER.html" style="color:#a5e1ff;font-weight:700;padding:8px">📘 Ana Plan · Fikirler · Canlı Görseller</a>
    <button class="tab active" data-tab="images" onclick="setTab('images')">Görseller & Test Renderları (<span id="cntImg">0</span>)</button>
    <button class="tab" data-tab="models" onclick="setTab('models')">3B Modeller / GLB (<span id="cntMod">0</span>)</button>
    <button class="tab" data-tab="docs" onclick="setTab('docs')">Planlar (.md) & Kodlar (<span id="cntDoc">0</span>)</button>
    <input type="search" id="filterBox" placeholder="Dosya veya klasör ara (ör. FAZ2, PLAN, fan)..." oninput="renderCurrent()">
    <button onclick="pollNow()">Şimdi Yenile</button>
  </div>
</header>
<main>
  <div class="status-bar">
    <span id="lastSync">Bağlanıyor...</span>
    <span>Otomatik canlı tarama: <b>her 2.5 saniyede bir</b> • <b>.md belgeleri biçimlendirilmiş Markdown olarak açılır</b></span>
  </div>
  <div id="contentArea"></div>
</main>

<div class="modal" id="modal">
  <div class="modal-top">
    <div id="modalTitle" style="font-weight:700;font-size:14px;word-break:break-all;"></div>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <button id="mdToggleBtn" style="display:none;" onclick="toggleMdRaw()">Ham Metin Göster</button>
      <a id="modalTabLink" class="link" target="_blank" style="padding:6px 10px;border:1px solid var(--border);border-radius:6px;">Yeni Sekmede Aç</a>
      <a id="modalDownloadLink" class="link" style="padding:6px 10px;border:1px solid var(--border);border-radius:6px;">İndir</a>
      <button onclick="closeModal()">Kapat (ESC)</button>
    </div>
  </div>
  <div class="modal-body" id="modalBody"></div>
</div>

<script>
let STATE = {{ images: [], models: [], docs: [] }};
let ACTIVE_TAB = 'images';
let LAST_TOP_MTIME = 0;
let CURRENT_DOC = {{ isMd: false, showingRaw: false, html: '', raw: '' }};

function fmtBytes(b) {{
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(2) + ' MB';
}}
function fmtAge(s) {{
  if (s < 5) return 'Az önce!';
  if (s < 60) return s + ' sn önce';
  if (s < 3600) return Math.floor(s / 60) + ' dk önce';
  return Math.floor(s / 3600) + ' sa önce';
}}
function esc(s) {{
  return String(s).replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
}}

function setTab(t) {{
  ACTIVE_TAB = t;
  document.querySelectorAll('.tab').forEach(el => el.classList.toggle('active', el.dataset.tab === t));
  renderCurrent();
}}

function rawUrl(path, mtime, extra) {{
  return 'raw/' + encodeURI(path) + '?v=' + encodeURIComponent(mtime) + (extra ? '&' + extra : '');
}}
function viewUrl(path, mtime) {{
  return 'view/' + encodeURI(path) + '?v=' + encodeURIComponent(mtime);
}}

function renderCurrent() {{
  const q = document.getElementById('filterBox').value.trim().toLowerCase();
  const box = document.getElementById('contentArea');
  if (ACTIVE_TAB === 'images') {{
    const items = STATE.images.filter(x => !q || x.path.toLowerCase().includes(q));
    box.innerHTML = '<div class="grid">' + items.map(it => {{
      const fresh = it.age_sec < 120;
      return `<div class="card ${{fresh ? 'fresh' : ''}}">
        <div class="thumb-wrap" onclick="openImage('${{esc(it.path)}}', '${{esc(it.mtime)}}')">
          <span class="badge ${{fresh ? 'new' : ''}}">${{fresh ? 'YENİ • ' : ''}}${{esc(fmtAge(it.age_sec))}}</span>
          <img loading="lazy" src="${{rawUrl(it.path, it.mtime)}}" alt="${{esc(it.name)}}">
        </div>
        <div class="meta">
          <div class="fname">${{esc(it.name)}}</div>
          <div class="fsub"><span>${{esc(it.folder)}}</span><span>${{fmtBytes(it.size)}}</span></div>
        </div>
      </div>`;
    }}).join('') + '</div>';
  }} else {{
    const src = ACTIVE_TAB === 'models' ? STATE.models : STATE.docs;
    const items = src.filter(x => !q || x.path.toLowerCase().includes(q));
    box.innerHTML = `<table class="list-table">
      <thead><tr><th>Dosya</th><th>Klasör</th><th>Boyut</th><th>Güncellenme</th><th>İşlem</th></tr></thead>
      <tbody>` + items.map(it => {{
        const isMd = it.ext === '.md';
        const pill = ACTIVE_TAB === 'docs'
          ? `<span class="ext-pill ${{isMd ? 'md' : ''}}">${{esc(it.ext.replace('.','').toUpperCase())}}</span>`
          : '';
        const nameCell = ACTIVE_TAB === 'docs'
          ? `<a class="link" href="#" onclick="openDoc('${{esc(it.path)}}', '${{esc(it.mtime)}}', ${{isMd}}); return false;">${{pill}}${{esc(it.name)}}</a>`
          : `<b>${{esc(it.name)}}</b>`;
        const openTabHref = isMd ? viewUrl(it.path, it.mtime) : rawUrl(it.path, it.mtime, 'raw=1');
        return `<tr>
          <td>${{nameCell}}</td>
          <td style="color:var(--muted)">${{esc(it.folder)}}</td>
          <td>${{fmtBytes(it.size)}}</td>
          <td>${{esc(fmtAge(it.age_sec))}}</td>
          <td style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
            ${{ACTIVE_TAB === 'docs' ? `<button onclick="openDoc('${{esc(it.path)}}', '${{esc(it.mtime)}}', ${{isMd}})">${{isMd ? '📄 Markdown Aç' : 'Oku'}}</button>` : ''}}
            ${{ACTIVE_TAB === 'docs' ? `<a class="link" href="${{openTabHref}}" target="_blank">Sekmede Aç</a>` : ''}}
            <a class="link" href="${{rawUrl(it.path, it.mtime, 'download=1')}}" download="${{esc(it.name)}}">İndir</a>
          </td>
        </tr>`;
      }}).join('') + `</tbody></table>`;
  }}
}}

function openImage(path, mtime) {{
  const url = rawUrl(path, mtime);
  document.getElementById('modalTitle').textContent = path;
  document.getElementById('mdToggleBtn').style.display = 'none';
  document.getElementById('modalTabLink').href = url;
  const dl = document.getElementById('modalDownloadLink');
  dl.href = rawUrl(path, mtime, 'download=1');
  dl.setAttribute('download', path.split('/').pop());
  const mb = document.getElementById('modalBody');
  mb.classList.add('img-mode');
  mb.innerHTML = `<img class="lightbox-img" src="${{url}}" onclick="this.classList.toggle('zoomed')" title="Tam boy yakınlaştırmak için tıkla">`;
  document.getElementById('modal').classList.add('open');
}}

async function openDoc(path, mtime, isMd) {{
  document.getElementById('modalTitle').textContent = path;
  const toggleBtn = document.getElementById('mdToggleBtn');
  toggleBtn.style.display = isMd ? 'inline-block' : 'none';
  toggleBtn.textContent = 'Ham Metin Göster';
  document.getElementById('modalTabLink').href = isMd ? viewUrl(path, mtime) : rawUrl(path, mtime, 'raw=1');
  const dl = document.getElementById('modalDownloadLink');
  dl.href = rawUrl(path, mtime, 'download=1');
  dl.setAttribute('download', path.split('/').pop());
  const mb = document.getElementById('modalBody');
  mb.classList.remove('img-mode');
  mb.innerHTML = '<div class="md-view">Yükleniyor...</div>';
  document.getElementById('modal').classList.add('open');

  if (isMd) {{
    const r = await fetch('api/render_md?path=' + encodeURIComponent(path) + '&v=' + encodeURIComponent(mtime));
    const data = await r.json();
    CURRENT_DOC = {{ isMd: true, showingRaw: false, html: data.html, raw: data.raw }};
    mb.innerHTML = `<article class="md-view">${{data.html}}</article>`;
  }} else {{
    const r = await fetch(rawUrl(path, mtime, 'raw=1'));
    const txt = await r.text();
    CURRENT_DOC = {{ isMd: false, showingRaw: true, html: '', raw: txt }};
    mb.innerHTML = '<pre class="doc-view"></pre>';
    mb.querySelector('pre').textContent = txt;
  }}
}}

function toggleMdRaw() {{
  if (!CURRENT_DOC.isMd) return;
  CURRENT_DOC.showingRaw = !CURRENT_DOC.showingRaw;
  const mb = document.getElementById('modalBody');
  const btn = document.getElementById('mdToggleBtn');
  if (CURRENT_DOC.showingRaw) {{
    btn.textContent = 'Markdown Görünümü';
    mb.innerHTML = '<pre class="doc-view"></pre>';
    mb.querySelector('pre').textContent = CURRENT_DOC.raw;
  }} else {{
    btn.textContent = 'Ham Metin Göster';
    mb.innerHTML = `<article class="md-view">${{CURRENT_DOC.html}}</article>`;
  }}
}}

function closeModal() {{
  document.getElementById('modal').classList.remove('open');
  document.getElementById('modalBody').innerHTML = '';
}}
window.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

async function pollNow() {{
  try {{
    const r = await fetch('api/state?t=' + Date.now(), {{ cache: 'no-store' }});
    const data = await r.json();
    STATE = data;
    document.getElementById('cntImg').textContent = data.images.length;
    document.getElementById('cntMod').textContent = data.models.length;
    document.getElementById('cntDoc').textContent = data.docs.length;
    const d = new Date(data.server_time * 1000);
    document.getElementById('lastSync').textContent = 'Canlı Bağlı • Son tarama: ' + d.toLocaleTimeString('tr-TR');
    const topMtime = Math.max(
      data.images[0]?.mtime || 0,
      data.models[0]?.mtime || 0,
      data.docs[0]?.mtime || 0
    );
    if (topMtime !== LAST_TOP_MTIME) {{
      LAST_TOP_MTIME = topMtime;
      renderCurrent();
    }} else if (ACTIVE_TAB === 'images') {{
      document.querySelectorAll('.card .badge').forEach((b, idx) => {{
        const q = document.getElementById('filterBox').value.trim().toLowerCase();
        const items = STATE.images.filter(x => !q || x.path.toLowerCase().includes(q));
        if (items[idx]) {{
          const fresh = items[idx].age_sec < 120;
          b.className = 'badge' + (fresh ? ' new' : '');
          b.textContent = (fresh ? 'YENİ • ' : '') + fmtAge(items[idx].age_sec);
        }}
      }});
    }}
  }} catch (err) {{
    document.getElementById('lastSync').textContent = 'Yeniden bağlanıyor...';
  }}
}}

pollNow();
setInterval(pollNow, 2500);
</script>
</body>
</html>
"""


class GalleryHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send_common_headers(
        self,
        code: int,
        ctype: str,
        length: int | None = None,
        cache: str = "no-cache",
        extra_headers: dict[str, str] | None = None,
    ):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", cache)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        if length is not None:
            self.send_header("Content-Length", str(length))
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        p = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if p in ("/", "/index.html"):
            # The project notebook is the sole public interface; the API below
            # supplies its live-images tab without a second gallery UI.
            body = (ROOT / "reports/AEGIS_GUNCEL_PLAN_VE_FIKIRLER.html").read_bytes()
            self._send_common_headers(200, "text/html; charset=utf-8", len(body))
            self.wfile.write(body)
            return

        if p == "/api/state":
            payload = json.dumps(scan_workspace(), ensure_ascii=False).encode("utf-8")
            self._send_common_headers(200, "application/json; charset=utf-8", len(payload))
            self.wfile.write(payload)
            return

        if p == "/api/render_md":
            rel = qs.get("path", [""])[0]
            target = is_safe_subpath(rel)
            if target is None or not target.is_file() or target.suffix.lower() != ".md":
                msg = b'{"error":"Not found"}'
                self._send_common_headers(404, "application/json; charset=utf-8", len(msg))
                self.wfile.write(msg)
                return
            md_text = target.read_text(encoding="utf-8", errors="replace")
            payload = json.dumps(
                {"html": render_markdown_to_html(md_text), "raw": md_text},
                ensure_ascii=False,
            ).encode("utf-8")
            self._send_common_headers(200, "application/json; charset=utf-8", len(payload))
            self.wfile.write(payload)
            return

        if p.startswith("/view/"):
            rel = urllib.parse.unquote(p[len("/view/"):])
            target = is_safe_subpath(rel)
            if target is None or not target.is_file():
                msg = b"404 Not Found"
                self._send_common_headers(404, "text/plain; charset=utf-8", len(msg))
                self.wfile.write(msg)
                return
            if target.suffix.lower() == ".md":
                md_text = target.read_text(encoding="utf-8", errors="replace")
                rel_norm = target.resolve().relative_to(ROOT).as_posix()
                body = build_standalone_md_page(rel_norm, md_text)
                self._send_common_headers(200, "text/html; charset=utf-8", len(body))
                self.wfile.write(body)
                return

        if p.startswith("/raw/"):
            rel = urllib.parse.unquote(p[len("/raw/"):])
            target = is_safe_subpath(rel)
            if target is None or not target.is_file():
                msg = b"404 Not Found"
                self._send_common_headers(404, "text/plain; charset=utf-8", len(msg))
                self.wfile.write(msg)
                return

            want_raw = qs.get("raw", ["0"])[0] == "1"
            want_dl = qs.get("download", ["0"])[0] == "1"

            # Direct browser navigation to /raw/*.md without ?raw=1 or ?download=1 ALSO opens formatted Markdown!
            if target.suffix.lower() == ".md" and not want_raw and not want_dl:
                md_text = target.read_text(encoding="utf-8", errors="replace")
                rel_norm = target.resolve().relative_to(ROOT).as_posix()
                body = build_standalone_md_page(rel_norm, md_text)
                self._send_common_headers(200, "text/html; charset=utf-8", len(body))
                self.wfile.write(body)
                return

            ctype, _ = mimetypes.guess_type(str(target))
            if target.suffix.lower() == ".glb":
                ctype = "model/gltf-binary"
            elif target.suffix.lower() == ".md" and want_dl:
                ctype = "text/markdown; charset=utf-8"
            elif target.suffix.lower() in {".md", ".lua", ".luau", ".py", ".txt"}:
                ctype = "text/plain; charset=utf-8"
            elif not ctype:
                ctype = "application/octet-stream"

            extra = {}
            if want_dl:
                extra["Content-Disposition"] = f'attachment; filename="{target.name}"'
            data = target.read_bytes()
            self._send_common_headers(200, ctype, len(data), cache="public, max-age=5", extra_headers=extra)
            self.wfile.write(data)
            return

        msg = b"404 Not Found"
        self._send_common_headers(404, "text/plain; charset=utf-8", len(msg))
        self.wfile.write(msg)


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), GalleryHandler)
    print(f"[GALLERY] Listening on http://0.0.0.0:{PORT} (Formatted Markdown enabled)", flush=True)
    srv.serve_forever()
