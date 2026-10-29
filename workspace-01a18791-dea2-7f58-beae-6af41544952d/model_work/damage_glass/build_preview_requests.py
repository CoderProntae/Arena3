"""Temporary Studio PLAY mesh requests, no persistence or edits to game scripts."""
import sys,json,os
from pathlib import Path
sys.path.insert(0,'/home/user/.cache/modeldeps')
import trimesh
ROOT=Path('/home/user'); OUT=ROOT/'.cache/glass_preview_rev2';OUT.mkdir(parents=True,exist_ok=True)
SID=os.environ['STUDIO_ID'] # Studio listesiyle her oturumda yenilenmeli
scene=trimesh.load(ROOT/'model_exports/DAMAGE_GLASS_NATURAL_REV2_CANDIDATE.glb',force='scene')
for i in range(1,4):
 m=scene.geometry[f'GLASS_LAYER_{i:02d}'];v=m.vertices;c=(v.min(axis=0)+v.max(axis=0))/2
 vs=','.join('{%.4f,%.4f,%.4f}'%(x-c[0],z-c[2],-(y-c[1])) for x,y,z in v)
 fs=','.join('{%d,%d,%d}'%(a+1,b+1,d+1) for a,b,d in m.faces)
 pos=(c[0],26.5+c[2],-c[1])
 code='''local A=game:GetService('AssetService')
local folder=workspace:FindFirstChild('__GLASS_PREVIEW_TEMP')
if not folder then folder=Instance.new('Folder');folder.Name='__GLASS_PREVIEW_TEMP';folder.Parent=workspace end
local name='GLASS_LAYER_%02d';assert(not folder:FindFirstChild(name),'duplicate')
local vs={%s};local fs={%s};local em=A:CreateEditableMesh();assert(em,'mesh budget')
local ids=table.create(#vs)
for i,v in ipairs(vs) do ids[i]=em:AddVertex(Vector3.new(v[1],v[2],v[3]));if i%%1000==0 then task.wait() end end
for i,t in ipairs(fs) do em:AddTriangle(ids[t[1]],ids[t[2]],ids[t[3]]);if i%%1000==0 then task.wait() end end
local status,content=A:CreateDataModelContentAsync(Content.fromObject(em));assert(status==Enum.CreateContentResult.Success and content,'content failed');em:Destroy()
local mp=A:CreateMeshPartAsync(content);mp.Name=name;mp.Anchored=true;mp.CanCollide=false;mp.CanQuery=false;mp.CanTouch=false;mp.CastShadow=false;mp.Color=Color3.fromRGB(155,176,188);mp.Material=Enum.Material.SmoothPlastic;mp.Transparency=0.50;mp.CFrame=CFrame.new(%.6f,%.6f,%.6f);mp.Parent=folder
return name..' CREATED'
'''%(i,vs,fs,*pos)
 (OUT/f'layer{i}.json').write_text(json.dumps({'studio_id':SID,'datamodel_type':'Server','code':code}))
 print(i,len(v),len(m.faces))
