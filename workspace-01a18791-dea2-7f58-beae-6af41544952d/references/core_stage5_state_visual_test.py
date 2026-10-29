"""Visual-state property checks with a local Lua stub; no mouse/click tests.

This runs the exact proposed game server in memory. Temporary state hooks and
preview flags exist only in the Lua string sent to the stub, never in Studio
or in any saved game source.
"""
from pathlib import Path
import sys
sys.path.insert(0, '/home/user/.cache/core_mock_deps')
from lupa import LuaRuntime

root = Path('/home/user')
boot = (root / '.cache/core_mock_boot_v3.lua').read_text()
source = (root / 'CORE_PROTOCOL_REMAKE_Server.server.lua').read_text()


def make(preview=False):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(boot)
    if preview:
        lua.execute('function __mock_services.RunService:IsStudio() return true end')
        s = source.replace('STUDIO_AUTO_MELTDOWN=false,', 'STUDIO_AUTO_MELTDOWN=true,', 1)
        s = s.replace('STUDIO_PREVIEW_SECOND=0,', 'STUDIO_PREVIEW_SECOND=244,', 1)
    else:
        s = source
    # Expose server state and entrypoint to validate startup without ever
    # firing ClickDetector events or driving an on-screen mouse cursor.
    marker = 'resetMachine()\nauditView()'
    assert s.count(marker) == 1
    s = s.replace(marker,
        '_G.__stage5_test={state=state,start=startReactor,emitters=emitters}\n'
        + marker, 1)
    lua.execute(s)
    return lua


def walk(lua, seconds, dt=0.2):
    for _ in range(round(seconds/dt)):
        lua.globals().__mock_step(dt)


def part(lua, name):
    item = lua.globals().__mock_find(name)
    assert item is not None, f'object absent: {name}'
    return item


def check_powered(lua, name, expected):
    o = part(lua, name)
    print(f'  {name}: transparency={o.Transparency:.3f}, expected {expected}')
    if expected == 'off':
        assert o.Transparency >= 0.94
    elif expected == 'on':
        assert o.Transparency <= 0.6


cold = make()
walk(cold, 1)
print('COLD after 1 sec:')
check_powered(cold, 'INCANDESCENT_VISIBLE_STAR', 'off')
check_powered(cold, 'SIX_ARMS_UPPER_WHITE_HOT_FILAMENT', 'off')
check_powered(cold, 'PHOTOSPHERE_WHITE_FUSION_TONGUE', 'off')
assert not part(cold, 'PROJECTOR_UPPER_PHOTONIC_WHITE_BEAM').Enabled
assert part(cold, 'EACH_LENS_FIRES_IN_ORDER').Emitted is None
state = cold.globals().__stage5_test.state
state.power = 25
state.powerIndex = 2
cold.globals().__stage5_test.start()
assert state.mode == 'STARTUP'
walk(cold, 11)
print('STARTUP at 11s:')
check_powered(cold, 'INCANDESCENT_VISIBLE_STAR', 'off')
assert cold.globals().__stage5_test.emitters[1].focusSparks.Emitted is None
assert cold.globals().__stage5_test.emitters[6].focusSparks.Emitted is None
walk(cold, 4)
print('STARTUP at 15s (first relay):')
assert cold.globals().__stage5_test.emitters[1].focusSparks.Emitted > 0
assert cold.globals().__stage5_test.emitters[6].focusSparks.Emitted is None
check_powered(cold, 'SIX_ARMS_UPPER_WHITE_HOT_FILAMENT', 'on')
check_powered(cold, 'INCANDESCENT_VISIBLE_STAR', 'off')
walk(cold, 15)
print('STARTUP at 30s (six relays + central ignition):')
assert cold.globals().__stage5_test.emitters[6].focusSparks.Emitted > 0
assert part(cold, 'INCANDESCENT_VISIBLE_STAR').Transparency < 0.92
walk(cold, 15)
print('ONLINE at 45s:')
assert state.mode in ('ONLINE', 'WARNING'), state.mode
check_powered(cold, 'INCANDESCENT_VISIBLE_STAR', 'on')

meltdown = make(preview=True)
walk(meltdown, 18)
print('STUDIO-ONLY 244s MELTDOWN PREVIEW after 18s:')
assert meltdown.globals().__stage5_test.state.mode == 'MELTDOWN'
print('  white-star transparency:', part(meltdown, 'INCANDESCENT_VISIBLE_STAR').Transparency)
assert part(meltdown, 'INCANDESCENT_VISIBLE_STAR').Transparency < 0.10
print('  core spoke transparency:', part(meltdown, 'PHOTOSPHERE_WHITE_FUSION_TONGUE').Transparency)
assert part(meltdown, 'PHOTOSPHERE_WHITE_FUSION_TONGUE').Transparency < 0.7
print('  visible plasma arc:', part(meltdown, 'CENTER_PLASMA_ARC_1').Transparency)
assert part(meltdown, 'CENTER_PLASMA_ARC_1').Transparency < 0.9
print('  room beam transparency:', part(meltdown, 'EDGE_EMERGENCY_BLUE_ARC').Transparency)
assert part(meltdown, 'EDGE_EMERGENCY_BLUE_ARC').Transparency > 0.9
print('COLD, sequenced STARTUP, 244s MELTDOWN VISUAL STATES: PASS (stub, not Studio)')
