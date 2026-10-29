#!/usr/bin/env python3
"""Package a narrowly scoped unattended Windows Studio bridge. No credentials.

The original manual-confirmation client stays untouched. The opt-in variant
allows ONLY start/stop Play and startup-specific multi_edit paths. Everything
else that formerly required YES is denied without blocking on input().
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
HERE=Path(__file__).resolve().parent
src=(HERE/'Roblox_Studio_MCP_Kalici_Kopru.py').read_text(encoding='utf-8')
policy='''\n# User-requested unattended STARTUP work only. This policy is ON in this\n# opt-in file; the old manual-confirmation client is never modified.\nAUTO_POLICY_MARKER="STARTUP_EDIT_PLAY_V1"\nKNOWN_STUDIO_ID="0a8ae564-fc7c-43d3-a625-b514c4f5a43f"\nSAFE_EXISTING={\n    "game.ServerScriptService.CORE_PROTOCOL_Server",\n    "game.ServerScriptService.REACTOR_MESH_CONTROLLER",\n    "game.StarterPlayer.StarterPlayerScripts.CORE_PROTOCOL_Client",\n}\nSAFE_PREFIXES=(\n    "game.ServerScriptService.STARTUP360_",\n    "game.ReplicatedStorage.STARTUP360_",\n    "game.StarterPlayer.StarterPlayerScripts.STARTUP360_",\n)\n\ndef unattended_startup_approval(tool: str, args: dict) -> bool:\n    """No blanket auto-YES. No publication, clicking or arbitrary Luau."""\n    if args.get("studio_id") != KNOWN_STUDIO_ID:\n        return False\n    if tool == "start_stop_play":\n        return set(args) == {"is_start", "studio_id"} and type(args["is_start"]) is bool\n    if tool != "multi_edit" or args.get("datamodel_type") != "Edit":\n        return False\n    path=args.get("file_path")\n    if not isinstance(path,str) or not (path in SAFE_EXISTING or\n            path.startswith(SAFE_PREFIXES)):\n        return False\n    if args.get("className") not in (None, "", "Script", "LocalScript", "ModuleScript"):\n        return False\n    edits=args.get("edits")\n    if not isinstance(edits,list) or not (1 <= len(edits) <= 60):\n        return False\n    if not all(isinstance(x,dict) and isinstance(x.get("old_string"),str)\n            and isinstance(x.get("new_string"),str) for x in edits):\n        return False\n    return len(json.dumps(args,ensure_ascii=False).encode("utf-8")) <= 350_000\n\ndef approval_without_prompts(tool: str, args: dict) -> bool:\n    allowed=unattended_startup_approval(tool,args)\n    print(f"[auto-policy] {'ALLOW' if allowed else 'DENY'} {tool}: "+\n          str(args.get("file_path") or args.get("is_start") or ""))\n    return allowed\n\n'''
anchor='\ndef announce_with_retries(bus: EncryptedBus, hello: dict) -> None:\n'
assert src.count(anchor)==1
src=src.replace(anchor,'\n'+policy+anchor)
needle='''    hello = {"kind": "HELLO", "session": session,\n             "tools": list(advertised.values()), "time": time.time()}'''
assert src.count(needle)==1
src=src.replace(needle,'''    hello = {"kind": "HELLO", "session": session,\n             "auto_policy": AUTO_POLICY_MARKER,\n             "tools": list(advertised.values()), "time": time.time()}''')
needle='''                if tool in APPROVAL_TOOLS and not local_approval(tool, arguments):\n                    raise MCPError("User denied this Studio operation")'''
assert src.count(needle)==1
src=src.replace(needle,'''                if tool in APPROVAL_TOOLS and not approval_without_prompts(tool, arguments):\n                    raise MCPError("Unattended STARTUP policy denied this operation")''')
needle='''    print("[bridge] Play, Luau, edits and player input require local YES per call.")'''
assert src.count(needle)==1
src=src.replace(needle,'''    print("[bridge] AUTO STARTUP POLICY: startup Edit scripts + Play start/stop ONLY.")\n    print("[bridge] Other mutating tools are DENIED without a prompt. No publication.")''')
src=src.replace('''"""Windows Studio MCP client; encrypted ntfy.envs.net mailbox, no inbound tunnel.\n\nRun ONLY on your own Windows PC. It starts the Roblox-provided local mcp.bat\nand makes outbound HTTPS requests. It does not open a server port or ask for\nRoblox credentials. The user must type YES separately for EACH mutating tool.\nProvider switch after old host daily quota reached. Same local-YES safeguard;\nkeep all three package files together. Ctrl+C to disconnect.\n"""''', '''"""User opt-in Windows Studio MCP client: unattended STARTUP work.\n\nOnly startup-specific script Edits and Play start/stop are auto-allowed.\nOther mutating tools are denied without console prompts. Read-only tools run\nautomatically as before. No publish tool is included. Ctrl+C disconnects.\nPlace next to existing Roblox_Studio_Bus.py and your SECRET configuration.\n"""''')
out=HERE/'Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py'
out.write_text(src,encoding='utf-8')
readme='''STARTUP OTOMATİK KÖPRÜ / kullanıcının açık isteğiyle hazırlanan sınırlı sürüm\n\n1) Windows'taki mevcut köprü terminalinde Ctrl+C.\n2) Bu ZIP içindeki Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py dosyasını\n   mevcut Roblox_Studio_MCP_Kalici_Kopru.py ile AYNI klasöre çıkar.\n   Roblox_Studio_Bus.py ve mevcut Roblox_Studio_MCP_Gizli_Ayar.json aynı klasörde\n   kalmalı. Gizli JSON'u ZIP'e koymadık; kimseyle paylaşma.\n3) Aynı klasörde Komut İstemi/PowerShell aç; çalıştır:\n   py -3 Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py\n   (py yoksa: python Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py)\n4) Terminalde 'AUTO STARTUP POLICY' ve 'ONLINE' çıktısı görülmeli.\n   Studio açık kalsın. Kapatmak için Ctrl+C. Eski elle-onaylı dosyaya\n   dönmek için bu işlemi durdurup eski dosyayı yeniden çalıştır.\n\nBu dosyada otomatik geçilenler:\n- yalnız seçili Studio örneğinde Play başlat/durdur;\n- yalnız Edit modunda CORE_PROTOCOL_Server, REACTOR_MESH_CONTROLLER,\n  CORE_PROTOCOL_Client veya adı STARTUP360_ ile başlayan açılış betikleri.\n\nBütün diğer düzenleme yolları, execute_luau, fare/klavye işlemleri ve gezinti\nonay istemeden REDDEDİLİR. Read-only araçlar zaten otomatik çalışır.\nYayınlama veya dosyaya .rbxlx kaydetme aracı yoktur; oyun publish edilmez.\nSunucunun 'oldu' demesi oyunun diske kaydedildiğini kanıtlamaz.\n\nGüvenlik: Daha geniş izin vermek için kodu değiştirme; banyodayken terminali\nızle. Uzaktan üçüncü taraf posta kutusundan şifreli komutlar taşınır;\nşifreli konfigürasyon dosyasını kimseyle paylaşma.\n'''
readme_path=HERE/'STARTUP_OTOMATIK_README.txt';readme_path.write_text(readme,encoding='utf-8')
archive=Path('/home/user/STARTUP_OTOMATIK_KOPRU.zip')
with ZipFile(archive,'w',compression=ZIP_DEFLATED) as z:
    z.write(out,out.name);z.write(readme_path,readme_path.name)
print(out.relative_to('/home/user'),out.stat().st_size,'bytes')
print(archive.relative_to('/home/user'),archive.stat().st_size,'bytes; NO secret JSON included')
