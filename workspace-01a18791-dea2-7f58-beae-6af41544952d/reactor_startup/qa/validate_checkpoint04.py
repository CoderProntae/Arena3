#!/usr/bin/env python3
"""Checkpoint 04: reproducible Studio evidence, not a substitute for the user's visual decision."""
from pathlib import Path
import hashlib,json,re,subprocess
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'reactor_startup/qa'
parser=ROOT/'.cache/luau/luau-compile'
files=[ROOT/'reactor_startup/source/ReactorPilot_SixHeads.server.lua',
       ROOT/'reactor_startup/source/ReactorPilot_CustomFlow.server.lua',
       ROOT/'reactor_startup/source/ReactorPilot_CustomVapor.client.lua',
       ROOT/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua',
       ROOT/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua',
       ROOT/'CORE_PROTOCOL_REMAKE_Client.client.lua']
for path in files:
    p=subprocess.run([str(parser),'--only-parse',str(path)],capture_output=True,text=True)
    assert p.returncode==0,(path,p.stderr)
for filename,key in [('checkpoint01_approval.json','user_selected'),
                     ('checkpoint02_approval.json','accepted'),
                     ('checkpoint03_approval.json','accepted')]:
    d=json.loads((QA/filename).read_text())
    assert d[key] in (True,'approve'),filename
pilot,server=files[0].read_text(),files[3].read_text()
assert 'CYAN_FUSION_HOLD_FOR_USER_APPROVAL' in pilot
assert 'PILOT_FUEL_SOCKET_' in pilot and 'r.socket;filament.Attachment1=focus' in pilot
assert 'glow.Attachment0=a;glow.Attachment1=b' in pilot
assert 'REACTOR_CORE_MANYETIK_01' in pilot
assert 'Instance.new("Part")' not in pilot and 'Instance.new("Sound")' not in pilot
assert 'SILENT_PROTOTYPE=true' in server
assert 'startupAge>=35.5+(i-1)*.62' in server
assert 'not e.broken' in server
assert 'tip:IsA("MeshPart")' in server
assert 'socket:IsA("Attachment")' in server
assert 'ReactorPilotStroke_' in server and 'ReactorPilotRelayTrace' in server
assert 'STUDIO_AUTO_STARTUP=false' in server
j=json.loads((QA/'checkpoint04_jobs.json').read_text())
for name in ('install_pilot04','install_r5_relays','cyan_core_volume_revision2',
             'cyan_approved_glb_core_revision3','opaque_approved_glb_focal_test_v4',
             'plasma_front_of_approved_core_v5','core_spatial_gpu_volume_v6',
             'initialize_cold_core_attr','test_auto_off','verify_auto_off'):
    assert j[name]['done'],name
readback=json.loads(Path(j['verify_auto_off']['response']).read_text())['response']['result']
readtext='\n'.join(x.get('text','') for x in readback['content'] if x['type']=='text')
assert readback['isError'] is False
assert 'STUDIO_AUTO_STARTUP=false' in readtext and 'STUDIO_AUTO_STARTUP=true' not in readtext

def evidence(name):
    job=json.loads((QA/name).read_text())
    assert all(job[k]['done'] for k in ('start','world','stop'))
    data=json.loads(Path(job['world']['response']).read_text())['response']['result']
    attrs=json.loads(next(x['text'] for x in data['content'] if x['type']=='text'))['attributes']
    return job,attrs
C,cold=evidence('checkpoint04_cold_final_attr.json')
assert cold['ReactorMode']=='COLD' and cold['ReactorPilotDarkness']==0
for k in ('ReactorPilotRelayMask','ReactorEmitterReadyMask',
          'ReactorPilotPhotonSources','ReactorPilotCyanVolume',
          'ReactorPilotCoreMeshActive','ReactorPilotCoreVolumeBeams',
          'ReactorPilotFuelNozzles'):
    assert cold[k]==0,(k,cold[k])
D,cyan=evidence('checkpoint04_core_volume_beams_v6_play.json')
assert D['frame']['done'] and D['volume_beam']['done']
assert cyan['ReactorMode']=='STARTUP' and cyan['ReactorStartupAge']>41
assert cyan['ReactorPilotStage']=='CYAN_FUSION_HOLD_FOR_USER_APPROVAL'
assert cyan['ReactorPilotReady'] is True and cyan['ReactorPilotHeadsAtTip']==6
assert cyan['ReactorPilotDarkness']==1
assert cyan['ReactorPilotRelayMask']==cyan['ReactorEmitterReadyMask']==63
assert cyan['ReactorPilotPhotonSources']==6
assert cyan['ReactorPilotCoreMeshActive']==6
assert cyan['ReactorPilotCoreVolumeBeams']==2
assert cyan['ReactorPilotCyanVolume']==1
assert cyan['ReactorPilotIgnitionTexture']=='PROCEDURAL_REPLICATED_CONTENT'
assert cyan['ReactorPilotFuelNozzles']==0 and cyan['ReactorPilotNewVisibleParts']==0
assert cyan['SilentPrototype'] is True
trace=cyan['ReactorPilotRelayTrace']
entries=[(int(m),float(t)) for m,t in re.findall(r'(\d+)@(\d+\.\d+)\|',trace)]
assert [m for m,t in entries]==[1,3,7,15,31,63],trace
assert all(entries[i][1]<entries[i+1][1] for i in range(5))
beam=json.loads(Path(D['volume_beam']['response']).read_text())['response']['result']
volume=json.loads(next(x['text'] for x in beam['content'] if x['type']=='text'))
assert volume['properties']['Enabled'] is True
P=ROOT/'reports/KONTROL_04_ALTI_GERCEK_LAZER_CYAN_CEKIRDEK_PLAY.jpg'
raw=Path(D['frame']['images'][0]);assert P.read_bytes()==raw.read_bytes()
assert hashlib.sha256(P.read_bytes()).hexdigest()==\
       '3e174bfbbb11b58f837bf276733495a36a05925e772d0c75e852a3d60d122646'
arr=np.asarray(Image.open(P).convert('RGB'),dtype=np.float32)
h,w=arr.shape[:2];assert (w,h)==(1228,722)
area=arr[135:515,w//2-280:w//2+280]
lum=area.mean(axis=2)
cyan_pixels=(area[:,:,1]>area[:,:,0]*1.3)&(area[:,:,2]>area[:,:,0]*1.3)&(area[:,:,1]>55)
assert float(cyan_pixels.mean())>.35 and float((lum>220).mean())<.10
print('PASS six Luau parse; 01/02/03 approvals preexist; 04 is technically playable')
print('PASS COLD 0 relay/laser/core, six real physical relays 1→3→7→15→31→63')
print('PASS six GLB-mouth lasers; approved-GLB cyan core; procedural GPU textures')
print(f'PASS genuine Studio Play image: chamber cyan {cyan_pixels.mean():.1%}, bright-white {float((lum>220).mean()):.1%}')
print('PASS Play stopped; Studio automatic startup OFF, no new visible Part/sound')
decision=json.loads((QA/'checkpoint04_approval.json').read_text())
assert decision['accepted'] is True
print('APPROVED by user with explicit note: solid-looking core needs effect-based treatment in 05.')
print('No white/ONLINE, manual START, video, publish or .rbxlx saved at 04.')
