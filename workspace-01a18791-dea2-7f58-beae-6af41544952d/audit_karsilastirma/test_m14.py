"""M14 yön ve çerçeve denetimi; GLB dosyalarını değiştirmez.
Çalıştır: PYTHONPATH=/home/user/.cache/modeldeps python audit_karsilastirma/test_m14.py
"""
import numpy as np
import trimesh
from pathlib import Path
root = Path('/home/user/model_exports')
old = trimesh.load(root/'DAMAGE_GLASS_FRACTURE_STAGES_01.glb', force='scene')
new = trimesh.load(root/'DAMAGE_GLASS_FRACTURE_STAGES_ADAY_YON_DUZELTME.glb', force='scene')
name='GLASS_STAGE3_CRAZED__glass_shard'
o=old.geometry[name]; n=new.geometry[name]; y=-46.625
assert len(o.faces)==len(n.faces)==72
assert o.vertices[:,1].mean() > y, 'Orijinal beklenen ters tarafta değil'
assert n.vertices[:,1].mean() < y, 'Aday oda tarafına yönelmiyor'
print('Yön testi: OK; author ortalama Y eski=%.4f aday=%.4f cam=%.4f' % (o.vertices[:,1].mean(), n.vertices[:,1].mean(),y))
for name,m in new.geometry.items():
 if 'crack_vein' not in name: continue
 t=m.vertices[m.faces]; total=sum(int(np.count_nonzero((t[:,:,0].min(axis=1)<x-0.21)&(t[:,:,0].max(axis=1)>x+0.21))) for x in (-11.25,11.25))
 print(name, 'dikme enini tamamen geçen üçgen sayısı:',total)
