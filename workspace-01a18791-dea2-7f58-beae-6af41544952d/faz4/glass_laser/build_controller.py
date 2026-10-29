"""Generate a server controller from approved M14 candidate GLB."""
import sys
from pathlib import Path
sys.path.insert(0,'/home/user/.cache/modeldeps')
import trimesh
R=Path('/home/user'); scene=trimesh.load(R/'model_exports/DAMAGE_GLASS_NATURAL_REV2_CANDIDATE.glb',force='scene')
parts=[]
for i in (1,2,3):
 m=scene.geometry[f'GLASS_LAYER_{i:02d}'];v=m.vertices;c=(v.min(axis=0)+v.max(axis=0))/2
 vs=','.join('{%.4f,%.4f,%.4f}'%(x-c[0],z-c[2],-(y-c[1])) for x,y,z in v)
 fs=','.join('{%d,%d,%d}'%(a+1,b+1,d+1) for a,b,d in m.faces)
 pos=(c[0],26.5+c[2],-c[1])
 parts.append('buildLayer(%d,{%s},{%s},Vector3.new(%.6f,%.6f,%.6f))'%(i,vs,fs,*pos))
head='''--!nonstrict
-- M14 GLASS LASER CONTROLLER / local candidate, not yet installed.
-- Server-authoritative ReactorMode/ReactorMeltdownAge; preview built from
-- user-reviewed additive 3D glass layers. No 2D overlays. Original core
-- owns the actual shatter at detonation; this controller never replaces it.
local A=game:GetService("AssetService")
local RunService=game:GetService("RunService")
local Debris=game:GetService("Debris")
local W=game:GetService("Workspace")
local S=game:GetService("ServerStorage")
local old=W:FindFirstChild("__M14_GLASS_LASER_VISUALS")
if old then old:Destroy() end
local folder=Instance.new("Folder");folder.Name="__M14_GLASS_LASER_VISUALS";folder.Parent=W
local layers={}
local function buildLayer(idx,vs,fs,pos)
 local em=A:CreateEditableMesh();assert(em,"EditableMesh allocation failed")
 local ok,content=pcall(function()
  local ids=table.create(#vs)
  for n,v in ipairs(vs) do ids[n]=em:AddVertex(Vector3.new(v[1],v[2],v[3]));if n%1000==0 then task.wait() end end
  for n,t in ipairs(fs) do em:AddTriangle(ids[t[1]],ids[t[2]],ids[t[3]]);if n%1000==0 then task.wait() end end
  local status,data=A:CreateDataModelContentAsync(Content.fromObject(em))
  assert(status==Enum.CreateContentResult.Success and data,"content conversion failed")
  return data
 end)
 pcall(function() em:Destroy() end)
 if not ok then error(content) end
 local mp=A:CreateMeshPartAsync(content);mp.Name="GlassDamageLayer_"..idx
 mp.Anchored=true;mp.CanCollide=false;mp.CanTouch=false;mp.CanQuery=false;mp.CastShadow=false
 mp.Color=Color3.fromRGB(155,176,188);mp.Material=Enum.Material.SmoothPlastic;mp.Transparency=1;mp.CFrame=CFrame.new(pos);mp.Parent=folder;layers[idx]=mp
end
local ok,err=pcall(function()
'''
tail='''
end)
if not ok then folder:Destroy();warn("[M14] geometry failed: "..tostring(err));return end
local function show(level)
 for i,p in ipairs(layers) do p.Transparency=i<=level and .50 or 1 end
 folder:SetAttribute("Stage",level)
end
local events={
 {at=143,level=1,x=-2.3,z=.5},
 {at=230,level=2,x=3.8,z=1.4},
 {at=327,level=3,x=-4.5,z=-3.1},
 {at=385,level=3,x=.9,z=-3.3},
 {at=434,level=3,x=0,z=0,final=true},
}
local function pulse(e)
 local origin=Vector3.new(0,26.5,2.7)
 local impact=Vector3.new(e.x,26.5+e.z,46.62)
 local delta=impact-origin;local size=e.final and 1.55 or .20
 local beam=Instance.new("Part");beam.Name=e.final and "FinalGlassLaser" or "GlassImpactLaser"
 beam.Anchored=true;beam.CanCollide=false;beam.CanTouch=false;beam.CanQuery=false;beam.CastShadow=false
 beam.Material=Enum.Material.Neon;beam.Color=e.final and Color3.fromRGB(225,245,255) or Color3.fromRGB(142,215,255)
 beam.Size=Vector3.new(size,size,delta.Magnitude);beam.CFrame=CFrame.lookAt((origin+impact)/2,impact);beam.Parent=folder
 Debris:AddItem(beam,e.final and 1.05 or .32)
 folder:SetAttribute("LastImpact",e.at);folder:SetAttribute("FinalImpact",e.final==true)
end
local lastMode,lastAge=nil,nil
local qaWorld=nil
if RunService:IsStudio() then
 local q=S:FindFirstChild("__M14_GLASS_QA")
 if q and q:IsA("BindableFunction") then
  q.OnInvoke=function(mode,age)
   if mode=="RELEASE" then qaWorld=nil;lastMode=nil;lastAge=nil;return "QA_RELEASED" end
   qaWorld={mode=tostring(mode),age=tonumber(age) or 0}
   return "QA_SET"
  end
 end
end
local con
con=RunService.Heartbeat:Connect(function()
 if not folder.Parent then if con then con:Disconnect() end;return end
 local world=W:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
 local mode,age
 if qaWorld then mode,age=qaWorld.mode,qaWorld.age
 elseif world then mode=world:GetAttribute("ReactorMode");age=world:GetAttribute("ReactorMeltdownAge") or 0
 else mode="COLD";age=0 end
 if mode=="MELTDOWN" then
  age=math.max(0,age)
  local level=0
  for _,e in ipairs(events) do if age>=e.at then level=math.max(level,e.level) end end
  show(level)
  -- Only crossing a threshold triggers a laser. Reconnecting late restores
  -- state but must not replay all past strikes at once.
  if lastMode=="MELTDOWN" and lastAge and age>=lastAge then
   for _,e in ipairs(events) do if lastAge<e.at and age>=e.at then pulse(e) end end
  end
  lastAge=age
 else
  show(0);lastAge=nil
  if mode~="AFTERMATH" then folder:SetAttribute("LastImpact",nil);folder:SetAttribute("FinalImpact",nil) end
 end
 lastMode=mode
end)
print("[M14] Glass laser controller ready")
'''
out=R/'faz4/glass_laser/M14_GlassLaser_CONTROLLER_CANDIDATE.server.lua';out.write_text(head+'\n'.join(parts)+tail)
print(out, out.stat().st_size)
