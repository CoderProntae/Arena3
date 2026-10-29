"""Yerel sözdizimi ve GLB sağlık kontrolü; Studio davranışını test etmez."""
from pathlib import Path
import subprocess, sys
import numpy as np, trimesh
root=Path('/home/user'); compiler=root/'.cache/luau-build/luau-compile'
if not compiler.exists():
    sys.exit('Luau derleyicisi yok (geçici .cache temizlenmiş olabilir).')
luas=[p for p in root.rglob('*.lua') if '.cache' not in p.parts]
for p in luas:
    result=subprocess.run([str(compiler),str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    if result.returncode: raise RuntimeError(f'{p}: {result.stderr}')
print('Luau syntax OK:',len(luas))
models=sorted((root/'model_exports').glob('*.glb'))
for p in models:
    scene=trimesh.load(p,force='scene')
    assert scene.geometry, p
    for name,m in scene.geometry.items():
        assert np.isfinite(m.vertices).all() and len(m.faces), (p,name)
        assert (m.area_faces>1e-10).all(), (p,name,'sıfır alanlı yüz')
print('GLB temel geometri OK:',len(models))
s=trimesh.load(root/'model_exports/DAMAGE_GLASS_NATURAL_CANDIDATE.glb',force='scene')
assert set(s.geometry)=={'GLASS_LAYER_01','GLASS_LAYER_02','GLASS_LAYER_03'}
for name,m in s.geometry.items():
    t=m.vertices[m.faces]
    for x in (-11.25,11.25):
        crossings=((t[:,:,0].min(axis=1)<x-.21)&(t[:,:,0].max(axis=1)>x+.21)).sum()
        assert not crossings,(name,x,crossings)
print('M14 aday: üç katman, dikmeyi baştan başa kesen üçgen yok')
