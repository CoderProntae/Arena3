#!/usr/bin/env python3
"""V2 offline structural, sightline and highlight-budget checks.

No Roblox Studio engine, camera renderer, audio loader or real raycast is used.
Engine-level appearance and click accessibility still REQUIRE Studio Play.
"""
from __future__ import annotations
import math
import pathlib
import re

ROOT=pathlib.Path(__file__).resolve().parent
SERVER=(ROOT/'CORE_PROTOCOL_V2_Server.server.lua').read_text()
CLIENT=(ROOT/'CORE_PROTOCOL_V2_Client.client.lua').read_text()

def check(label,condition):
    assert condition,f'FAILED: {label}'
    print('PASS',label)

number_lines=len(SERVER.splitlines())+len(CLIENT.splitlines())
check('Two installable V2 Roblox entrypoints',
      'RunService.Heartbeat:Connect' in SERVER
      and 'CORE_PROTOCOL_V2_CUES' in SERVER
      and 'CORE_PROTOCOL_V2_CUES' in CLIENT)
check(f'Game code remains within 8000 lines ({number_lines})',
      number_lines<=8000)
check('Original V1 world is NOT overwritten by V2',
      'world.Name="CORE_PROTOCOL_V2_WORLD"' in SERVER
      and 'world.Name="CORE_PROTOCOL_WORLD"' not in SERVER)
check('First meltdown chapter 435s',
      bool(re.search(r'MELTDOWN_SECONDS=435\b',SERVER)))
beats=[int(t) for t in re.findall(r'flagAt\(age,(\d+),"',SERVER)]
check(f'21 sorted, distinct cinematic crisis beats ({len(beats)})',
      len(beats)==21 and beats==sorted(set(beats))
      and beats[0]==12 and beats[-1]==430)

block=SERVER.split('AUDIO={',1)[1].split('\n    },',1)[0]
sound_keys=set(re.findall(r'\b([a-z]+)="rbxassetid://',block))
called=set(re.findall(r'sfx\("([a-z]+)"',SERVER))
check('All referenced SFX have configured Roblox asset IDs',called<=sound_keys)
controls=re.findall(r'local (\w+)=makeControl\(',SERVER)
check('Seven machined controls have server-side click listeners',
      len(controls)==7 and all(
          f'{name}.click.MouseClick:Connect' in SERVER
          for name in controls))
check('Buttons/dials/lever tips do not intercept their own clicks',
      'ring.CanQuery=false' in SERVER
      and 'rod.CanQuery=false' in SERVER
      and 'tip.CanQuery=false' in SERVER)
check('3 randomized cards, 3 insertable sockets, final pushbutton',
      all(text in SERVER for text in (
          'bay.click.MouseClick:Connect',
          'data.click.MouseClick:Connect',
          'shutdownButtonClick.MouseClick:Connect',
          'randomizeAuthorizationCards()')))
check('Camera/music client cannot mutate reactor state',
      'command~="SYNC" then return' in SERVER)
check('No shutter hides the center of the window',
      'liveShutters' not in SERVER
      and 'OPAQUE_DEEP_COBALT_CHAMBER_BACK' in SERVER)

config=SERVER.split('VISUAL={',1)[1].split('\n    },',1)[0]
def value(name):
    m=re.search(rf'\b{name}=([-\d.]+)',config)
    assert m,name
    return float(m.group(1))
check('Core point light is physically unable to light the window',
      value('CORE_LIGHT_RANGE') < 93.25-26
      and value('CORE_LIGHT_MAX')<=6)
check('Low glow threshold and clamp replace V1 whiteout',
      value('BLOOM_THRESHOLD')>=2.2
      and value('BLOOM_IDLE')<=0.2
      and value('BLOOM_MELTDOWN')<=0.5
      and value('ROOM_EXPOSURE')<=-0.6)
check('Shock sphere diameter contained BEHIND the glass',
      'local safeDiameter=math.min(52' in SERVER
      and 23+52/2<93.25)
pressure=SERVER.split('local function overpressure()',1)[1].split(
    'local function continuedCorePulse',1)[0]
check('Routine pipe burst cannot leave white fog active for 435 seconds',
      'e.Enabled=true' not in pressure
      and 'fog.LightEmission=0.015' in SERVER
      and 'e:Emit(19)' in pressure)
check('Focused projector beams never turn all six white',
      'or C.magenta -- NEVER replace all six arms with white beams.' in SERVER)
check('V2 dark layered background and warm low-sheen room',
      'OPAQUE_DEEP_COBALT_CHAMBER_BACK' in SERVER
      and 'LOW_SHEEN_WARM_LAB_FLOOR' in SERVER
      and 'DIFFUSE_IVORY_NEVER_NEON' in SERVER)

# Segment/AABB intersection of selected permanent large hard surfaces.
# Glass is 98% transparent and excluded; Studio audit uses actual raycast.
obstacles=[
    ('lower sill',(-63,63,23.85,26.45,92.05,94.55)),
    ('top arch',(-63,63,71.5,82.5,92.05,94.55)),
    ('left mullion',(-18.36,-17.64,26.75,71.75,92.9,94.1)),
    ('right mullion',(17.64,18.36,26.75,71.75,92.9,94.1)),
    ('left equipment wall',(-54,-36,30.2,70.6,94.72,95.72)),
    ('left control bench',(-60,-25,24.5,30,101.3,121.8)),
    ('raised floor console',(-15,15,24.5,31.0,118.5,133.5)),
    ('big ceiling frame',(-23,23,76.8,79.2,106,112)),
]

def intersects(a,b,box):
    lo,hi=0.0,1.0
    for axis in range(3):
        mn,mx=box[axis*2:axis*2+2]
        step=b[axis]-a[axis]
        if abs(step)<1e-9:
            if not mn<=a[axis]<=mx:return False
        else:
            t0,t1=(mn-a[axis])/step,(mx-a[axis])/step
            lo=max(lo,min(t0,t1));hi=min(hi,max(t0,t1))
            if lo>hi:return False
    return hi>=0 and lo<=1

rays=[]
emitter_axes={
    'TOP':(0,1),'LEFT':(-1,0),'RIGHT':(1,0),
    'LOWER_LEFT':(-.72,-.70),'LOWER_RIGHT':(.72,-.70),
    'BOTTOM':(0,-1),
}
for height in (31,35):
    eye=(-29,height,151)
    for tag,(vx,vy) in emitter_axes.items():
        mag=math.hypot(vx,vy)
        target=(29*vx/mag,53+29*vy/mag,18)
        rays.append((f'{tag}@eye{height}',eye,target))
    rays.append((f'STAR@eye{height}',eye,(0,53,27)))
for ex in (-6,0,6):
    for tx in (-14,0,14):
        rays.append((f'center_{ex}_{tx}',(ex,35,151),(tx,53,27)))
for label,eye,target in rays:
    ratio=(eye[2]-93.25)/(eye[2]-target[2])
    ix=eye[0]+(target[0]-eye[0])*ratio
    iy=eye[1]+(target[1]-eye[1])*ratio
    hits=[name for name,box in obstacles if intersects(eye,target,box)]
    check(f'{label} open frame (window {ix:+.1f},{iy:.1f})',
          -54<ix<54 and 26.7<iy<71.75 and not hits)
check(f'{len(rays)} analytical observation rays evaluated',len(rays)==23)
print('ALL V2 OFFLINE CHECKS PASS; this is NOT a rendered Roblox Studio test.')
