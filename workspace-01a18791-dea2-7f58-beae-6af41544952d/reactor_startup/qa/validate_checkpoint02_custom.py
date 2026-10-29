#!/usr/bin/env python3
"""Technical checks for custom flow. Does NOT certify visual reference quality."""
from pathlib import Path
import json, subprocess, hashlib
R=Path(__file__).resolve().parents[2]
compiler=R/'.cache/luau/luau-compile'
source=R/'reactor_startup/source'
files=[source/'ReactorPilot_SixHeads.server.lua',
       source/'ReactorPilot_CustomFlow.server.lua',
       source/'ReactorPilot_CustomVapor.client.lua',
       R/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua',
       R/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua',
       R/'CORE_PROTOCOL_REMAKE_Client.client.lua']
for file in files:
    test=subprocess.run([str(compiler),'--only-parse',str(file)],capture_output=True,text=True)
    assert test.returncode==0,(str(file),test.stderr)
s=files[0].read_text();v=files[1].read_text();c=files[2].read_text()
assert 'NOZZLE__white' in s and 'PILOT_FUEL_SOCKET_' in s
assert 'Instance.new("ParticleEmitter")' not in s
assert 'CreateDataModelContentAsync' in v and 'math.noise' in v
assert 'gpu.TextureContent=content' in v and 'beam.TextureContent=content' in v
assert 'PILOT_OWN_IMAGE_WORLD_MOTION_' in v and 'LockedToPart=false' in v
assert 'RunService.Heartbeat' in v and 'PILOT_FLOW_ADVECTED_TIP_' in v
assert 'WritePixelsBuffer' in c and 'RunService.RenderStepped' in c
assert all('rbxasset://textures/particles/smoke_main.dds' not in x for x in (s,v,c))
assert all('DEBUG_ONLY_' not in x for x in (s,v,c))
assert all('Instance.new("Part")' not in x and 'Instance.new("Sound")' not in x
           for x in (s,v,c))
assert json.loads((R/'reactor_startup/qa/checkpoint01_approval.json').read_text())['user_selected']=='approve'

def attributes(job_file):
    jobs=json.loads((R/'reactor_startup/qa'/job_file).read_text())
    assert jobs['start']['done'] and jobs['world']['done'] and jobs['stop']['done']
    payload=json.loads(Path(jobs['world']['response']).read_text())
    result=payload['response']['result'];assert result['isError'] is False
    attrs=json.loads(next(x['text'] for x in result['content'] if x['type']=='text'))['attributes']
    return jobs, attrs

jobs=json.loads((R/'reactor_startup/qa/checkpoint02_custom_jobs.json').read_text())
for stage in ('pilot_custom','client_renderer','world_flow_renderer','world_flow_gpu',
              'physical_flow_revision','physical_light_revision',
              'client_depth_restored','debug_billboard_removed',
              'server_gui_probe_removed','test_auto_off','verify_auto_off'):
    assert jobs[stage]['done'],stage
sourceRead=json.loads(Path(jobs['verify_auto_off']['response']).read_text())
lines='\n'.join(x.get('text','') for x in sourceRead['response']['result']['content']
                if x.get('type')=='text')
assert 'STUDIO_AUTO_STARTUP=false' in lines and 'STUDIO_AUTO_STARTUP=true' not in lines

C,cold=attributes('checkpoint02_custom_final_cold.json')
assert C['cold_frame']['done']
assert cold['ReactorMode']=='COLD' and cold['ReactorPilotStage']=='COLD'
for key in ('ReactorPilotFuelNozzles','ReactorPilotCustomSmokeRate',
            'ReactorPilotCustomGpuBackends','ReactorPilotFlowBeamStrands',
            'ReactorPilotPhotonSources','ReactorPilotStockSmokeEmitters'):
    assert cold[key]==0,(key,cold[key])

F,fuel=attributes('checkpoint02_custom_final_preview.json')
assert fuel['ReactorMode']=='STARTUP' and fuel['ReactorStartupAge']>=18
assert fuel['ReactorPilotStage']=='FUEL_HOLD_FOR_USER_APPROVAL'
assert fuel['ReactorPilotHeadsAtTip']==6 and fuel['ReactorPilotFuelNozzles']==6
assert fuel['ReactorPilotCustomGpuBackends']==6
assert fuel['ReactorPilotFlowBeamStrands']==17
assert fuel['ReactorPilotFlowTexture']=='PROCEDURAL_REPLICATED_CONTENT'
assert fuel['ReactorPilotStockSmokeEmitters']==0
assert fuel['ReactorPilotPhotonSources']==0 and fuel['ReactorEmitterReadyMask']==0
assert fuel['ReactorPilotNewVisibleParts']==0 and fuel['SilentPrototype']
assert 0<fuel['ReactorPilotCustomSmokeRate']<=26
frames=[]
for key in ('frame1','frame2'):
    assert F[key]['done'] and len(F[key]['images'])==1
    frame=Path(F[key]['images'][0]);assert frame.is_file() and frame.stat().st_size>10000
    frames.append(hashlib.sha256(frame.read_bytes()).hexdigest())
assert frames[0]!=frames[1], 'Expected two separate actual Play frames'
log=json.loads(Path(F['console']['response']).read_text())
text='\n'.join(x['text'] for x in log['response']['result']['content'] if x['type']=='text')
assert '[PILOT FLOW] Original signed-noise image baked' in text
assert '[PILOT VFX] renderer=PROCEDURAL_EDITABLE_IMAGE' in text
assert '[PILOT FLOW] 17 moving streams and 6 own-image GPU backends' in text
print('PASS six sources parse; custom procedural image baked into replicated Content')
print('PASS COLD no emission, photons or ribbons; real fuel Play has 6 GLBs, 6 custom textured backends and 17 streams')
print('PASS two different real Studio Play frames, console, no stock smoke asset, no new Part or sound')
print('PASS Play stopped; Studio auto-start restored OFF and re-read')
print('PENDING user verdict on motion/reference aesthetics: two stills are NOT video proof')
print('NOTE no manual click, screenshot motion, later phases, save or publish claimed')
