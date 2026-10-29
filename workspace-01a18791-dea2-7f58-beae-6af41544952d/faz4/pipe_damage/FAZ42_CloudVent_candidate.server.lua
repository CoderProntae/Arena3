--!nonstrict
-- FAZ 4.2: authoritative pipe breaks -> reviewed M13 spool + physical 3D vent.
-- Does not change coolant math or existing pipe damage flags. It reads only
-- ReactorPipeBrokenMask (R5 line IDs): UL=line6, UR=line3, RL=line8, RR=line1.
local RunService=game:GetService('RunService')
local AssetService=game:GetService('AssetService')
local Workspace=game:GetService('Workspace')
local ServerStorage=game:GetService('ServerStorage')
local assembly=Workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',60)
if not assembly then warn('[FAZ42] assembly missing');return end
local static=assembly:WaitForChild('STATIC',30)
if not static then warn('[FAZ42] STATIC missing');return end
local old=assembly:FindFirstChild('__FAZ42_VENT_3D')
if old then old:Destroy() end
local root=Instance.new('Folder');root.Name='__FAZ42_VENT_3D';root.Parent=assembly
-- A reusable multi-lobed 3D cloud: overlapping uneven closed shells, with
-- smooth radial normals. No cone, Beam, billboard or ParticleEmitter.
local function buildVent()
 local em=AssetService:CreateEditableMesh();assert(em,'vent EditableMesh unavailable')
 local ok,content=pcall(function()
  local N,R=16,10
  local lobes={
   {0,0,0,.44},{.37,.08,.04,.30},{-.34,.09,-.04,.29},
   {.04,.30,.10,.31},{-.10,-.29,.06,.28},{.09,-.03,.34,.28},{-.13,.04,-.30,.29},
  }
  for l,v in ipairs(lobes) do
   local rings,normals={},{}
   for j=1,R-1 do
    rings[j]={};normals[j]={};local phi=-math.pi/2+math.pi*j/R
    for i=0,N-1 do
     local theta=i*math.pi*2/N
     local direction=Vector3.new(math.cos(phi)*math.cos(theta),math.sin(phi),math.cos(phi)*math.sin(theta))
     local mod=1+.09*math.sin(theta*3+phi*4+l*1.3)+.06*math.sin(theta*5-phi*3+l)
     rings[j][i+1]=em:AddVertex(Vector3.new(v[1],v[2],v[3])+direction*(v[4]*mod))
     normals[j][i+1]=em:AddNormal(direction)
    end
   end
   local bottom=em:AddVertex(Vector3.new(v[1],v[2]-v[4],v[3]));local bn=em:AddNormal(Vector3.new(0,-1,0))
   local top=em:AddVertex(Vector3.new(v[1],v[2]+v[4],v[3]));local tn=em:AddNormal(Vector3.new(0,1,0))
   local function face(a,b,c,na,nb,nc)
    local f=em:AddTriangle(a,b,c);em:SetFaceNormals(f,{na,nb,nc})
   end
   for i=1,N do
    local k=i%N+1
    face(bottom,rings[1][i],rings[1][k],bn,normals[1][i],normals[1][k])
    face(top,rings[R-1][k],rings[R-1][i],tn,normals[R-1][k],normals[R-1][i])
   end
   for j=1,R-2 do for i=1,N do
    local k=i%N+1
    local a,b,c,d=rings[j][i],rings[j][k],rings[j+1][i],rings[j+1][k]
    local na,nb,nc,nd=normals[j][i],normals[j][k],normals[j+1][i],normals[j+1][k]
    face(a,c,b,na,nc,nb);face(b,c,d,nb,nc,nd)
   end end
  end
  local status,data=AssetService:CreateDataModelContentAsync(Content.fromObject(em))
  assert(status==Enum.CreateContentResult.Success and data,'vent mesh conversion failed');return data
 end)
 pcall(function() em:Destroy() end)
 if not ok then error(content) end
 local p=AssetService:CreateMeshPartAsync(content);p.Name='VENT_CLOUD_TEMPLATE'
 p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false
 p.Material=Enum.Material.SmoothPlastic;p.Color=Color3.fromRGB(198,223,230)
 p.Transparency=1;p.DoubleSided=true;p.Parent=root
 return p
end
local ok,template=pcall(buildVent)
if not ok then root:Destroy();warn('[FAZ42] vent failed: '..tostring(template));return end
template.Parent=nil
local specs={{id='UPPER_LEFT',bit=5,upper=true},{id='UPPER_RIGHT',bit=2,upper=true},{id='REAR_LEFT',bit=7},{id='REAR_RIGHT',bit=0}}
local bindings={}
local function bind(spec)
 local piping=static:FindFirstChild('REACTOR_COOLANT_PIPING_RING_01')
 local kit=static:FindFirstChild('DAMAGE_PIPE_RUPTURE_KIT_01')
 local intact=piping and piping:FindFirstChild('PIPE_SPOOL_'..spec.id)
 local damaged=kit and kit:FindFirstChild('PIPE_SPOOL_'..spec.id..'_RUPTURED')
 if not intact or not damaged then return nil end
 local a=damaged:FindFirstChild('MOUTH_A');local b=damaged:FindFirstChild('MOUTH_B')
 if not a or not b then return nil end
 -- Producers create models before their async MeshParts. Never snapshot an
 -- incomplete spool, or later children could remain visible after rupture.
 local ni,nd=0,0
 for _,p in ipairs(intact:GetDescendants()) do if p:IsA('MeshPart') then ni+=1 end end
 for _,p in ipairs(damaged:GetDescendants()) do if p:IsA('MeshPart') then nd+=1 end end
 if ni~=6 or nd~=8 then return nil end
 local v={id=spec.id,bit=spec.bit,intact=intact,damaged=damaged,original={},vents={}}
 for _,p in ipairs(intact:GetDescendants()) do if p:IsA('BasePart') then v.original[p]={p.Transparency,p.CanCollide,p.CanTouch,p.CanQuery} end end
 for _,anchor in ipairs({a,b}) do
  for n=1,4 do
   local plume=template:Clone();plume.Name='VENT_'..spec.id..'_'..anchor.Name..'_'..n;plume.Parent=root
   v.vents[#v.vents+1]={p=plume,anchor=anchor,index=n}
  end
 end
 return v
end
local function apply(v,broken)
 for p,original in pairs(v.original) do if p.Parent then
  p.Transparency=broken and 1 or original[1];p.CanCollide=not broken and original[2];p.CanTouch=not broken and original[3];p.CanQuery=not broken and original[4]
 end end
 for _,p in ipairs(v.damaged:GetDescendants()) do if p:IsA('MeshPart') then p.Transparency=broken and 0 or 1 end end
 for _,vent in ipairs(v.vents) do vent.p.Transparency=1 end
 v.active=broken;v.damaged:SetAttribute('Faz42Active',broken)
end
local elapsed=0;local qaMask=nil;local connection
if RunService:IsStudio() then
 local q=ServerStorage:FindFirstChild('__FAZ42_PIPE_QA')
 if q and q:IsA('BindableFunction') then q.OnInvoke=function(mask) if mask=='RELEASE' then qaMask=nil else qaMask=tonumber(mask) or 0 end return 'OK' end end
end
connection=RunService.Heartbeat:Connect(function(dt)
 if not root.Parent then connection:Disconnect();return end
 elapsed+=math.min(dt,.2);if elapsed<.12 then return end
 local t=os.clock();elapsed=0
 local world=Workspace:FindFirstChild('CORE_PROTOCOL_V2_WORLD')
 local mask=qaMask or (world and world:GetAttribute('ReactorPipeBrokenMask')) or 0
 for _,spec in ipairs(specs) do
  local v=bindings[spec.id]
  if v and (not v.intact.Parent or not v.damaged.Parent) then
   for _,x in ipairs(v.vents) do x.p:Destroy() end;bindings[spec.id]=nil;v=nil
  end
  if not v then v=bind(spec);bindings[spec.id]=v end
  if v then
   local broken=math.floor(mask/2^spec.bit)%2==1
   if v.active~=broken then apply(v,broken) end
   if broken then for _,x in ipairs(v.vents) do
    local pos=x.anchor.Position
    local inward=pos.X<0 and 1 or -1
    local dy=spec.upper and -.5 or .45
    local dir=Vector3.new(inward,dy,.25).Unit
    local phase=(t*.55+(x.index-1)/4+spec.bit*.071)%1
    local travel=.15+2.7*phase
    local rise=.38*phase*phase
    local swirl=.10*math.sin(t*2+x.index*2+spec.bit)
    local offset=Vector3.new(swirl,rise,.10*math.cos(t*1.6+x.index))
    local width=.22+phase*.91
    x.p.Size=Vector3.new(width,width*(.90+.10*math.sin(t+x.index)),width)
    x.p.CFrame=CFrame.new(pos+dir*travel+offset)*CFrame.Angles(t*.22+x.index,phase*2,t*.16+spec.bit)
    x.p.Transparency=.97-.18*math.sin(math.pi*phase)
   end end
  end
 end
 root:SetAttribute('PipeMask',mask)
end)
print('[FAZ42] Pipe damage visual controller ready')
