"""Engineering-only Ruby/Lua surrogate. NOT Roblox Studio."""
import pathlib, sys, time
sys.path.insert(0,"/home/user/.cache/core_mock_deps")
from lupa import LuaRuntime
root=pathlib.Path('/home/user')
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'.cache/core_mock_boot_v3.lua').read_text())
try:
    lua.execute((root/'CORE_PROTOCOL_REMAKE_Server.server.lua').read_text())
    print('MOCK: server initialized; objects:',len(lua.eval('__mock_services.Workspace:GetDescendants()')))
    lua.execute((root/'CORE_PROTOCOL_REMAKE_Client.client.lua').read_text())
    print('MOCK: client initialized; UI/render bound')
except Exception as ex:
    raise RuntimeError('Error during stubbed initialization (not Studio)') from ex
step=lua.globals().__mock_step
click=lua.globals().__mock_click_control
read=lua.globals().__mock_find
sent=lua.globals().__mock_sent
base=time.time()

def run(seconds,dt=.1):
    for _ in range(round(seconds/dt)):
        step(dt)

def captions():
    source=read('OVER_WINDOW_EMERGENCY_LETTERBOX_LIT_SCREEN')
    engrave=source.FindFirstChild(source,'ENGRAVED_VIEW')
    label=engrave.FindFirstChild(engrave,'INSCRIPTION')
    return label.Text

def act(control):
    click(control)
    step(.7)
    print('  click',control,'->',captions())

print('MOCK initial:',captions())
run(1)
print('MOCK after initial heartbeat:',captions())
act('REACTOR_POWER')
act('INITIAL_STARTUP')
run(47)
print('MOCK startup 47s:',captions())
assert 'NOMINAL' in captions(), captions()
act('HEATING_LASERS')
for _ in range(3):act('REACTOR_POWER')
for _ in range(3):act('COOLANT')
run(25)
print('MOCK after heating:',captions(), 'music=',len(sent))
assert 'FAILURE' in captions(), captions()
act('COOLANT') # from zero to 25 percent; sufficient to actually SCRAM safely
act('GUARDED_SCRAM')
print('MOCK early SCRAM:',captions())
assert 'SHUTDOWN' in captions(), captions()
run(78)
print('MOCK after successful shutdown reset:',captions())
assert 'STANDBY' in captions(), captions()
# Prepare a faster direct round to exercise 21 crisis events and detonation.
for _ in range(4):act('REACTOR_POWER')
act('INITIAL_STARTUP')
act('HEATING_LASERS')
run(46)
for _ in range(3):act('COOLANT') # do not starve coolant DURING startup
run(26)
print('MOCK failure round start:',captions())
assert 'FAILURE' in captions(), captions()
run(434)
print('MOCK after 434s:',captions(),'sounds/events=',len(sent))
assert 'CONTAINMENT LOST' in captions(), captions()
run(58)
print('MOCK after explosion reset:',captions())
assert 'STANDBY' in captions(), captions()
# Roblox automatically respawns a player killed outside the bunker.
lua.execute('__mock_humanoid.Health=100')
# Explicit failed startup path.
act('REACTOR_POWER')
act('INITIAL_STARTUP')
for _ in range(4):act('REACTOR_POWER') # 25 -> 0
run(16)
print('MOCK failed startup:',captions())
assert 'IGNITION FAILED' in captions(), captions()
run(19)
assert 'STANDBY' in captions(), captions()
# Freezedown and recovery (normal25%/50% online start).
act('REACTOR_POWER')
act('INITIAL_STARTUP')
run(45)
for _ in range(2):act('COOLANT') # 50 -> 100
for _ in range(4):act('REACTOR_POWER') # 25 -> 0
run(48)
print('MOCK freezedown:',captions())
assert 'FREEZEDOWN' in captions(), captions()
act('INITIAL_STARTUP') # ignition recovers freezer via laser and power
run(30)
print('MOCK recovery:',captions())
assert 'NOMINAL' in captions() or 'HEAT RISING' in captions(), captions()
act('EMERGENCY_COOLANT')
run(4)
readout=read('LEFT_COOLANT_STATUS_LIT_SCREEN')
label=readout.FindFirstChild(readout,'ENGRAVED_VIEW')
label=label.FindFirstChild(label,'INSCRIPTION')
print('MOCK emergency reserve:',label.Text)
assert 'E-COOL 09' in label.Text, label.Text
act('EMERGENCY_COOLANT') # manual shutoff
act('GUARDED_SCRAM') # coolant remains 100
assert 'SHUTDOWN' in captions(), captions()
run(77)
assert 'STANDBY' in captions(), captions()
# Three scattered authorization cards, three working slots and plunger.
act('REACTOR_POWER')
act('INITIAL_STARTUP')
run(46)
collect=lua.globals().__mock_collect_cards
assert collect()==3
run(4)
click_part=lua.globals().__mock_click
for i in range(1,4):
    click_part(f'CARD_SOCKET_CLICKABLE_CONTACT_{i}')
    step(.6)
click_part('HEAVY_FINAL_SHUTDOWN_PLUNGER')
run(2)
print('MOCK three-card shutdown:',captions())
assert 'SHUTDOWN' in captions(), captions()
run(77)
assert 'STANDBY' in captions(), captions()
# A late SCRAM must damage hardware; player in bunker survives explosion.
for _ in range(4):act('REACTOR_POWER')
act('INITIAL_STARTUP')
act('HEATING_LASERS')
run(46)
for _ in range(3):act('COOLANT')
run(30)
assert 'FAILURE' in captions(), captions()
run(272)
act('GUARDED_SCRAM')
print('MOCK late SCRAM:',captions())
assert 'SHUTDOWN FAILURE' in captions(), captions()
lua.execute('__mock_root.CFrame=CFrame.new(0,28,200)')
run(166)
print('MOCK bunker after blast, humanoid health:',lua.eval('__mock_humanoid.Health'), 'mode:', captions())
assert lua.eval('__mock_humanoid.Health') == 100
assert 'CONTAINMENT LOST' in captions(), captions()
# LocalScript audiovisual event handling/rendering: not a real Roblox camera.
lua.execute('''
local remote=__mock_services.ReplicatedStorage:FindFirstChild('CORE_PROTOCOL_V2_CUES')
remote.OnClientEvent:Fire('MUSIC','START',0,'rbxassetid://1843973421',
 __mock_services.Workspace:GetServerTimeNow(),__mock_services.Workspace:GetServerTimeNow())
remote.OnClientEvent:Fire('SHAKE',2.1,3.0)
remote.OnClientEvent:Fire('FLASH',0.55,'red')
__mock_services.RunService._render(0.016)
remote.OnClientEvent:Fire('MUSIC','CROSSFADE',0,'rbxassetid://9040229071',
 __mock_services.Workspace:GetServerTimeNow(),__mock_services.Workspace:GetServerTimeNow())
remote.OnClientEvent:Fire('MUSIC','STOP')
remote.OnClientEvent:Fire('RESET')
__mock_services.RunService._render(0.016)
''')
print('MOCK client music, shake, flash, crossfade, stop and render: OK')
print('MOCK all server scenarios simulated in',round(time.time()-base,2),'s')
# V3 lens renderer: no actual Glass in the panoramic window or SCRAM cover.
panes=[p for p in lua.eval('__mock_services.Workspace:GetDescendants()').values()
       if str(p.Name).startswith('PANORAMIC_LAMINATED_GLASS_')]
assert len(panes)==2 and all(p.Material=='Material.SmoothPlastic' for p in panes)
input_service=lua.eval('game:GetService("UserInputService")')
input_service.InputBegan.Fire(input_service.InputBegan, lua.eval('{KeyCode=Enum.KeyCode.V}'), False)
assert lua.eval('__mock_player.CameraMode') == 'CameraMode.Classic'
input_service.InputBegan.Fire(input_service.InputBegan, lua.eval('{KeyCode=Enum.KeyCode.V}'), False)
assert lua.eval('__mock_player.CameraMode') == 'CameraMode.LockFirstPerson'
print('MOCK R2 glass renderer and V camera toggle: OK')
