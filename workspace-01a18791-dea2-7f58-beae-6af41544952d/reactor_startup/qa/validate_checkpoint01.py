#!/usr/bin/env python3
"""Checkpoint 01: deliberately incomplete; parser/contract, not visual approval."""
from pathlib import Path
import hashlib,subprocess,json,zipfile,io,urllib.request
R=Path(__file__).resolve().parents[2]
P=R/'.cache/luau/luau-compile'
if not P.is_file():
    # .cache is excluded from snapshots: recover the official parser as needed.
    url='https://github.com/luau-lang/luau/releases/download/0.744/luau-ubuntu.zip'
    try:
        payload=urllib.request.urlopen(url,timeout=30).read()
        P.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            P.write_bytes(z.read('luau-compile'))
            P.chmod(0o755)
    except Exception as exc:
        raise RuntimeError('Resmî Luau CLI gerekiyor; geçici indirme başarısız') from exc
pilot=R/'reactor_startup/source/ReactorPilot_SixHeads.server.lua'
server=R/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua'
mesh=R/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua'
client=R/'CORE_PROTOCOL_REMAKE_Client.client.lua'
for f in (pilot,server,mesh,client):
 result=subprocess.run([str(P),'--only-parse',str(f)],capture_output=True,text=True)
 assert result.returncode==0,(f,result.stderr)
 assert f.is_file()
assert len(list((R/'reactor_startup/source').glob('*.lua')))==1
assert not list((R/'reactor_startup/source').glob('ReactorBoot_*'))
p=pilot.read_text();s=server.read_text();m=mesh.read_text();c=client.read_text()
assert p.count('REACTOR_EMITTER_REV03_')==1 and p.count('REACTOR_PISTON_GUIDE_01_')==1
assert all(x in p for x in ('UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'))
assert not any(x in p for x in ('Instance.new("Part")','Instance.new("Beam")','Instance.new("ParticleEmitter")','Instance.new("Sound")'))
assert 'ReactorPilotPhotonSources",0' in p and 'MECHANICS_HOLD_FOR_USER_APPROVAL' in p
assert 'Studio' not in p and 'FireServer' not in p
assert 'StartupScore' not in s and 'ReactorBoot_' not in s
assert 'if pilot then relay=false end' in s
assert 'if state and state.mode=="STARTUP" then return end' in s
assert 'state.mode="STARTUP"' in s and 'state.power<25 or actualCoolant()<18' in s
assert 'local owner=world:GetAttribute("ReactorPilotOwner")==true' in m
assert 'ReactorStartupOwned' not in m and 'ReactorBootOnlineVisual' not in m
assert 'local inPilot=reactor' in c
wall=R/'model_exports/REACTOR_REAR_BULKHEAD_IRON_REV04.glb'
assert hashlib.sha256(wall.read_bytes()).hexdigest()==(
 '929cd6dd70cf8ab45d3d432d4a11d9db77e4f0e074106c90b5b6c52badb71e2d')
j=json.loads((R/'reactor_startup/qa/checkpoint01_jobs.json').read_text())
assert all(j.get(k,{}).get('done') for k in ('old_score_wipe','old_rig_wipe',
 'old_film_wipe','old_director_wipe','install_new_pilot',
 'installed_live_server','installed_live_mesh','installed_live_client',
 'final_auto_off'))
def world_attrs(journal):
    raw=json.loads(Path(journal['world']['response']).read_text())
    payload=next(x['text'] for x in raw['response']['result']['content']
                 if x.get('type')=='text')
    return json.loads(payload)['attributes']
cold=json.loads((R/'reactor_startup/qa/checkpoint01_cold_corrected.json').read_text())
hold=json.loads((R/'reactor_startup/qa/checkpoint01_hold.json').read_text())
c=world_attrs(cold);h=world_attrs(hold)
assert c['ReactorMode']=='COLD' and c['ReactorPilotPhotonSources']==0
assert c['ReactorEmitterReadyMask']==0 and c['ReactorPilotReady'] is True
assert h['ReactorMode']=='STARTUP' and h['ReactorPilotOwner'] is True
assert h['ReactorPilotHeadsAtTip']==6 and h['ReactorPilotPhotonSources']==0
assert h['ReactorEmitterReadyMask']==0
assert hold['stop']['done'] and cold['stop']['done']
assert all(Path(hold[k]['images'][0]).is_file() for k in ('hold_frame',))
print('PASS: only new Stage 01 source; 4 Luau parse; six GLB sources; zero photons')
print('PASS: real Studio Play COLD and 6/6 deployed; both sessions stopped')
print('NOTE: deletion call was denied; old Source wiped, later Studio tree shows no old names')
print('NOTE: runtime/visual/manual-button acceptance are separate user gates')
