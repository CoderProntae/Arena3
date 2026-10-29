#!/usr/bin/env python3
"""Final technical gate for six GLB-mouth vapor sources; subjective visuals remain user-owned."""
from pathlib import Path
import json, subprocess, hashlib
R=Path(__file__).resolve().parents[2]
qa=R/'reactor_startup/qa'
source=R/'reactor_startup/source'
parser=R/'.cache/luau/luau-compile'
files=[source/'ReactorPilot_SixHeads.server.lua',
       source/'ReactorPilot_CustomFlow.server.lua',
       source/'ReactorPilot_CustomVapor.client.lua',
       R/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua',
       R/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua',
       R/'CORE_PROTOCOL_REMAKE_Client.client.lua']
for file in files:
    result=subprocess.run([str(parser),'--only-parse',str(file)],capture_output=True,text=True)
    assert result.returncode==0,(file,result.stderr)
pilot,flow,client=(f.read_text() for f in files[:3])
assert 'tip.Position-r.site.axis*.09' in pilot and 'NOZZLE__white' in pilot
assert 'socket.CFrame=tip.CFrame:ToObjectSpace(CFrame.lookAt' in pilot
assert 'entry.CFrame=tip.CFrame:ToObjectSpace(CFrame.new(socket.WorldPosition))' in flow
assert 'local origin=socket.WorldPosition' in flow
assert 'assert(#allBeams==6 and #rasterBackends==6' in flow
assert 'gpu.TextureContent=content' in flow and 'CreateDataModelContentAsync' in flow
assert 'WritePixelsBuffer' in client and 'RunService.RenderStepped' in client
for s in (pilot,flow,client):
    assert 'rbxasset://textures/particles/smoke_main.dds' not in s
    assert 'DEBUG_ONLY_' not in s
    assert 'Instance.new("Part")' not in s and 'Instance.new("Sound")' not in s
assert json.loads((qa/'checkpoint01_approval.json').read_text())['user_selected']=='approve'
feedback=json.loads((qa/'checkpoint02_custom_feedback2.json').read_text())
assert feedback['accepted'] is False and feedback['user_decision']=='revise'

def read_attributes(jobfile):
    jobs=json.loads((qa/jobfile).read_text())
    assert jobs['start']['done'] and jobs['world']['done'] and jobs['stop']['done']
    raw=json.loads(Path(jobs['world']['response']).read_text())
    res=raw['response']['result'];assert res['isError'] is False
    obj=json.loads(next(x['text'] for x in res['content'] if x['type']=='text'))
    return jobs,obj['attributes']

jobs=json.loads((qa/'checkpoint02_nozzle_center_jobs.json').read_text())
for key in ('pilot','world_vfx','client_vfx','world_vfx_front_nozzle',
            'client_vfx_front_nozzle','world_vfx_six_jets',
            'final_auto_off','final_verify_auto_off'):
    assert jobs[key]['done'],key
read=json.loads(Path(jobs['final_verify_auto_off']['response']).read_text())
text='\n'.join(x.get('text','') for x in read['response']['result']['content']
               if x['type']=='text')
assert 'STUDIO_AUTO_STARTUP=false' in text and 'STUDIO_AUTO_STARTUP=true' not in text
C,cold=read_attributes('checkpoint02_six_distinct_nozzle_cold.json')
assert cold['ReactorMode']=='COLD' and cold['ReactorPilotStage']=='COLD'
for key in ('ReactorPilotFuelNozzles','ReactorPilotCustomGpuBackends',
            'ReactorPilotFlowBeamStrands','ReactorPilotPhotonSources'):
    assert cold[key]==0,(key,cold[key])
F,fuel=read_attributes('checkpoint02_six_distinct_nozzle_jets.json')
assert fuel['ReactorMode']=='STARTUP' and fuel['ReactorStartupAge']>=18
assert fuel['ReactorPilotStage']=='FUEL_HOLD_FOR_USER_APPROVAL'
assert fuel['ReactorPilotHeadsAtTip']==fuel['ReactorPilotFuelNozzles']==6
assert fuel['ReactorPilotCustomGpuBackends']==fuel['ReactorPilotFlowBeamStrands']==6
assert fuel['ReactorPilotFlowTexture']=='PROCEDURAL_REPLICATED_CONTENT'
assert fuel['ReactorPilotStockSmokeEmitters']==0
assert fuel['ReactorPilotNewVisibleParts']==0
assert fuel['ReactorPilotPhotonSources']==fuel['ReactorEmitterReadyMask']==0
assert fuel['SilentPrototype']
assert F['fuel_frame']['done'] and len(F['fuel_frame']['images'])==1
image=Path(F['fuel_frame']['images'][0]);assert image.stat().st_size>10000
log=json.loads(Path(F['console']['response']).read_text())
console='\n'.join(x['text'] for x in log['response']['result']['content'] if x['type']=='text')
assert '[PILOT FLOW] Original signed-noise image baked' in console
assert '[PILOT FLOW] 6 moving streams and 6 own-image GPU backends' in console
assert '[PILOT VFX] renderer=PROCEDURAL_EDITABLE_IMAGE' in console
# Read-only Studio inspection of ALL original six ring MeshParts: each 0.15-stud thick.
inspections=json.loads((qa/'checkpoint02_nozzle_inspect.json').read_text())
for tag in ('left','right','upper','lower_left','lower_right','lower'):
    raw=json.loads(Path(inspections[tag]['response']).read_text())
    obj=json.loads(next(x['text'] for x in raw['response']['result']['content'] if x['type']=='text'))
    assert obj['className']=='MeshPart' and obj['name']=='NOZZLE__white'
    thickness=float(obj['properties']['Size'].split(',')[0])
    assert abs(thickness-.15)<.01,(tag,thickness)
# Two independent in-Play socket readings to catch offset or axis errors.
play=json.loads((qa/'checkpoint02_nozzle_center_play.json').read_text())
for key in ('left_socket','lowerleft_socket'):
    raw=json.loads(Path(play[key]['response']).read_text())
    obj=json.loads(next(x['text'] for x in raw['response']['result']['content'] if x['type']=='text'))
    local=float(obj['properties']['CFrame.Position'].split(',')[0])
    assert abs(local+.09)<.001,(key,local)
print('PASS six original GLB rings inspected: 0.15-stud face; actual nozzle-center sockets at -0.09 local X')
print('PASS real fuel Play: 6 heads, 6 custom bitmap backends, 6 separate streams, 0 photons; screenshot saved')
print('PASS COLD zero fuel/VFX; Play stopped; auto-start reset OFF; all 6 scripts parse')
print('PENDING user visual approval and live motion feel; no manual input, save or publish claimed')
