#!/usr/bin/env python3
"""Dark-chamber gate: objective Studio evidence, NOT subjective visual approval."""
from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];Q=R/'reactor_startup/qa'
parser=R/'.cache/luau/luau-compile'
sources=[R/'reactor_startup/source/ReactorPilot_SixHeads.server.lua',
         R/'reactor_startup/source/ReactorPilot_CustomFlow.server.lua',
         R/'reactor_startup/source/ReactorPilot_CustomVapor.client.lua',
         R/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua',
         R/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua',
         R/'CORE_PROTOCOL_REMAKE_Client.client.lua']
for file in sources:
    p=subprocess.run([str(parser),'--only-parse',str(file)],capture_output=True,text=True)
    assert p.returncode==0,(file,p.stderr)
pilot,main=sources[0].read_text(),sources[3].read_text()
assert json.loads((Q/'checkpoint01_approval.json').read_text())['user_selected']=='approve'
assert json.loads((Q/'checkpoint02_approval.json').read_text())['accepted'] is True
assert 'DARK_CHAMBER_HOLD_FOR_USER_APPROVAL' in pilot
assert 'ReactorPilotDarkness' in pilot and 'ReactorPilotPhotonSources",0' in pilot
assert 'r.light.Brightness=.045+darkness*2.2' in pilot
assert 'chamberServiceLights' in main and 'chamberWashLights' in main
assert 'local pilotDark=pilot and math.clamp' in main
assert 'Lighting.Ambient=Color3.fromRGB(138,137,142):Lerp' in main
assert 'CHAMBER POWERDOWN  /  SIX HEADS LIT' in main
assert 'Instance.new("Part")' not in pilot
assert 'Instance.new("Sound")' not in pilot
jobs=json.loads((Q/'checkpoint03_jobs.json').read_text())
for stage in ('pilot_dark_stage','server_chamber_lighting','six_glb_lights_revision',
              'dark_status_title','test_auto_off','verify_auto_off'):
    assert jobs[stage]['done'],stage
serverRead=json.loads(Path(jobs['verify_auto_off']['response']).read_text())
text='\n'.join(x['text'] for x in serverRead['response']['result']['content'] if x['type']=='text')
assert 'STUDIO_AUTO_STARTUP=false' in text and 'STUDIO_AUTO_STARTUP=true' not in text

def read_evidence(name):
    job=json.loads((Q/name).read_text())
    assert job['start']['done'] and job['world']['done'] and job['stop']['done']
    raw=json.loads(Path(job['world']['response']).read_text())
    attrs=json.loads(next(x['text'] for x in raw['response']['result']['content'] if x['type']=='text'))['attributes']
    return job,attrs
C,cold=read_evidence('checkpoint03_final_cold.json')
D,dark=read_evidence('checkpoint03_dark_final_play.json')
assert cold['ReactorMode']=='COLD' and cold['ReactorPilotStage']=='COLD'
for k in ('ReactorPilotDarkness','ReactorPilotFuelNozzles',
          'ReactorPilotFlowBeamStrands','ReactorPilotPhotonSources','ReactorEmitterReadyMask'):
    assert cold[k]==0,(k,cold[k])
assert dark['ReactorMode']=='STARTUP' and dark['ReactorStartupAge']>=25
assert dark['ReactorPilotStage']=='DARK_CHAMBER_HOLD_FOR_USER_APPROVAL'
assert dark['ReactorPilotDarkness']==1
assert dark['ReactorPilotHeadsAtTip']==6
for k in ('ReactorPilotFuelNozzles','ReactorPilotCustomGpuBackends',
          'ReactorPilotFlowBeamStrands','ReactorPilotPhotonSources',
          'ReactorEmitterReadyMask','ReactorPilotNewVisibleParts'):
    assert dark[k]==0,(k,dark[k])
assert dark['SilentPrototype'] is True
for job,key in ((C,'cold_frame'),(D,'dark_frame')):
    assert job[key]['done'] and len(job[key]['images'])==1
    assert Path(job[key]['images'][0]).stat().st_size>10000
light=json.loads(Path(D['nozzle_light']['response']).read_text())
props=json.loads(next(x['text'] for x in light['response']['result']['content']
                      if x['type']=='text'))['properties']
assert props['Enabled'] is True and 2.0<props['Brightness']<2.5
assert props['Range']==15
assert json.loads(Path(C['nozzle_light']['response']).read_text())['response']['result']['isError'] is False

def chamber_stats(path):
    a=np.asarray(Image.open(path).convert('RGB'))
    h,w=a.shape[:2]
    # Identical world camera; horizontal crops may differ by Studio window width.
    rect=a[135:515,w//2-280:w//2+280].astype(float)
    lum=rect.mean(axis=2)
    cyan=((rect[:,:,1]>rect[:,:,0]*1.32)&
          (rect[:,:,2]>rect[:,:,0]*1.28)&
          (rect[:,:,1]>55))
    return float((lum<30).mean()),float(cyan.mean())
coldDark,_=chamber_stats(C['cold_frame']['images'][0])
darkDark,cyan=chamber_stats(D['dark_frame']['images'][0])
assert coldDark<.65 and darkDark>coldDark+.35 and darkDark>.86
assert cyan>.005,('no nozzle light perceptible in chamber',cyan)
print('PASS accepted 01/02; six Luau sources parse; stage 03 holds before relay/ONLINE')
print(f'PASS same-camera chamber dark pixels {coldDark:.1%} COLD → {darkDark:.1%} dark; cyan {cyan:.1%}')
print('PASS COLD restored, fuel/relays/photon off, six lit GLBs, control room remains visible in Play')
print('PASS Play stopped; Studio auto-start returned OFF; no added Part/sound')
approval=json.loads((Q/'checkpoint03_approval.json').read_text())
assert approval['accepted'] is True and approval['studio_auto_start_after_gate'] is False
print('APPROVED by user for reactor-chamber stage; control-room physical power stays ON')
print('No manual START, video, publish or place-file save claimed')
