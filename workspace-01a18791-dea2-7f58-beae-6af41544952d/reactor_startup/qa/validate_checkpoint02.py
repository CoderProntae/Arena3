#!/usr/bin/env python3
"""Second visual gate. This cannot certify subjective visual similarity."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[2]
compiler=R/'.cache/luau/luau-compile'
assert compiler.is_file(), 'Run validate_checkpoint01.py once to fetch Luau CLI'
script=R/'reactor_startup/source/ReactorPilot_SixHeads.server.lua'
server=R/'CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua'
mesh=R/'model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua'
client=R/'CORE_PROTOCOL_REMAKE_Client.client.lua'
for f in (script,server,mesh,client):
    result=subprocess.run([str(compiler),'--only-parse',str(f)],
                          capture_output=True,text=True)
    assert result.returncode==0,(str(f),result.stderr)
s=script.read_text()
assert 'PILOT_FUEL_SOCKET_' in s and 'NOZZLE__white' in s
assert 'totalBudget<=110' in s and 'if not active then' in s
assert 'vapor.Parent=socket' in s and 'stopFuel()' in s
assert 'ReactorPilotPhotonSources",0' in s
assert not any(x in s for x in ('Instance.new("Part")',
 'Instance.new("Beam")','Instance.new("Sound")'))
assert json.loads((R/'reactor_startup/qa/checkpoint01_approval.json').read_text())['user_selected']=='approve'
p=R/'reactor_startup/qa/checkpoint02_jobs.json'
j=json.loads(p.read_text())
assert j['pilot']['done'] and j['server']['done'] and j['test_auto_on']['done']
C=json.loads((R/'reactor_startup/qa/checkpoint02_cold.json').read_text())
raw=json.loads(Path(C['world']['response']).read_text())
c=json.loads(next(x['text'] for x in raw['response']['result']['content']
                  if x.get('type')=='text'))['attributes']
assert C['stop']['done'] and c['ReactorMode']=='COLD'
assert c['ReactorPilotFuelNozzles']==0 and c['ReactorPilotParticleBudget']==0
assert j['fuel_revision3']['done'] and j['test_auto_off_corrected']['done']
assert j['verify_auto_off']['done']
source=json.loads(Path(j['verify_auto_off']['response']).read_text())
text='\n'.join(x.get('text','') for x in source['response']['result']['content']
               if x.get('type')=='text')
assert 'STUDIO_AUTO_STARTUP=false' in text and 'STUDIO_AUTO_STARTUP=true' not in text
F=json.loads((R/'reactor_startup/qa/checkpoint02_fuel_revision3_hold.json').read_text())
assert F['start']['done'] and F['world']['done'] and F['fuel_frame']['done'] and F['stop']['done']
raw=json.loads(Path(F['world']['response']).read_text())
a=json.loads(next(x['text'] for x in raw['response']['result']['content']
                  if x.get('type')=='text'))['attributes']
assert a['ReactorMode']=='STARTUP' and a['ReactorStartupAge']>=18
assert a['ReactorPilotStage']=='FUEL_HOLD_FOR_USER_APPROVAL'
assert a['ReactorPilotHeadsAtTip']==6 and a['ReactorPilotFuelNozzles']==6
assert 0<a['ReactorPilotParticleBudget']<=110
assert a['ReactorPilotPhotonSources']==0 and a['ReactorEmitterReadyMask']==0
assert a['ReactorPilotNewVisibleParts']==0 and a['SilentPrototype']
assert len(F['fuel_frame']['images'])==1 and Path(F['fuel_frame']['images'][0]).is_file()
print('PASS real Studio Play at fuel hold: 6/6 GLB heads/nozzles, capped vapor, no photons')
print('PASS sources parse, cold zero fuel, Studio auto-start restored to OFF, Play stopped')
print('PENDING user visual approval: pale vapor appears but does not match reference density')
print('NOTE no manual click, reference quality, later phases, saving or publish proven')
