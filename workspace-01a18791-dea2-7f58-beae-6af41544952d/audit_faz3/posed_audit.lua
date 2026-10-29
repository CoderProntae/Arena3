assert(game.Name=="AEGIS_Reactor.rbxlx", "yanlis oyun")
local WS=game:GetService("Workspace")
local RS=game:GetService("RunService")
assert(RS:IsEdit(), "Edit degil")
local H=game:GetService("HttpService")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local moving=assembly:WaitForChild("MOVING")
local staticRoot=assembly:WaitForChild("STATIC")

local sites={
 {tag="UPPER", axis=Vector3.new(0,1,0)},
 {tag="LEFT", axis=Vector3.new(-1,0,0), hatch=1},
 {tag="RIGHT", axis=Vector3.new(1,0,0), hatch=-1},
 {tag="LOWER_LEFT", axis=Vector3.new(-0.72,-0.694,0).Unit},
 {tag="LOWER_RIGHT", axis=Vector3.new(0.72,-0.694,0).Unit},
 {tag="LOWER", axis=Vector3.new(0,-1,0)},
}
local function M(parent,name)
 local it=parent:FindFirstChild(name)
 assert(it and it:IsA("Model"), "yok: "..name)
 return {item=it, at=it:GetPivot()}
end
local rigs={}
for _,s in sites do
 local head=M(moving,"REACTOR_EMITTER_REV03_"..s.tag)
 local motor=M(moving,"REACTOR_PISTON_GUIDE_01_"..s.tag)
 local st={}
 for _,pc in ipairs({"STAGE1","STAGE2","STAGE3","PUSHER"}) do st[pc]=M(motor.item,pc) end
 local doors=nil
 if s.hatch then
  local hm=M(moving,"REACTOR_WALL_HATCH_THROUGH_01_"..s.tag)
  doors={a=M(hm.item,"LEAF_LEFT"), b=M(hm.item,"LEAF_RIGHT")}
 end
 rigs[#rigs+1]={site=s, head=head, stages=st, doors=doors}
end
local radials={}
for _,ch in moving:GetChildren() do
 if ch:IsA("Model") and ch.Name:find("RADIAL_HATCH") then
  local l=ch:FindFirstChild("LEAF_LEFT") local r=ch:FindFirstChild("LEAF_RIGHT")
  if l and r then radials[#radials+1]={name=ch.Name, left={item=l, at=l:GetPivot()}, right={item=r, at=r:GetPivot()}} end
 end
end
local rotor=moving:FindFirstChild("REACTOR_REAR_TURBINE_ROTOR")
assert(rotor, "rotor yok")
local rotorHome=rotor:GetPivot()

-- grup haritasi: ayni site (emitör+piston+duvar kapagi) = ayni grup; radyal kendi grubu; rotor kendi; STATIC = "STATIC"
local groupOf={}
local function topModel(inst)
 local cur=inst
 while cur and cur.Parent~=moving and cur.Parent~=staticRoot and cur.Parent~=assembly and cur.Parent~=WS do cur=cur.Parent end
 return cur
end
local function groupName(inst)
 local t=topModel(inst)
 if not t then return "?" end
 if t.Parent==staticRoot then return "STATIC."..t.Name end
 for _,r in rigs do
  if t==r.head.item then return "SITE."..r.site end
 end
 return t.Name
end
-- piston/hatch top modellerini site'a bagla
local topGroup={}
for _,r in rigs do
 local motor=moving:FindFirstChild("REACTOR_PISTON_GUIDE_01_"..r.site.tag)
 if motor then topGroup[motor]="SITE."..r.site.tag end
 topGroup[r.head.item]="SITE."..r.site.tag
 local hm=moving:FindFirstChild("REACTOR_WALL_HATCH_THROUGH_01_"..r.site.tag)
 if hm then topGroup[hm]="SITE."..r.site.tag end
end
local function gName(inst)
 local t=topModel(inst)
 if not t then return "?" end
 if t.Parent==staticRoot then return "STATIC."..t.Name end
 if t.Parent==moving then return topGroup[t] or t.Name end
 return t.Name
end

local savedFid={}
local function applyPose(gate, stroke, rotorRad)
 for _,r in rigs do
  local ax=r.site.axis
  r.stages.STAGE1.item:PivotTo(CFrame.new(-ax*(6.6*stroke))*r.stages.STAGE1.at)
  r.stages.STAGE2.item:PivotTo(CFrame.new(-ax*(13.2*stroke))*r.stages.STAGE2.at)
  local push=CFrame.new(-ax*(19.8*stroke))
  r.stages.STAGE3.item:PivotTo(push*r.stages.STAGE3.at)
  r.stages.PUSHER.item:PivotTo(push*r.stages.PUSHER.at)
  r.head.item:PivotTo(push*r.head.at)
  if r.doors then
   local slide=r.site.hatch*5.85*gate
   r.doors.a.item:PivotTo(CFrame.new(0,0,slide)*r.doors.a.at)
   r.doors.b.item:PivotTo(CFrame.new(0,0,-slide)*r.doors.b.at)
  end
 end
 for _,rh in radials do
  local slide=5.85*gate
  rh.left.item:PivotTo(CFrame.new(0,0,slide)*rh.left.at)
  rh.right.item:PivotTo(CFrame.new(0,0,-slide)*rh.right.at)
 end
 rotor:PivotTo(CFrame.new(rotorHome.Position)*CFrame.Angles(0,0,rotorRad))
end
local function restorePose()
 applyPose(0,0,0)
 rotor:PivotTo(rotorHome)
end

local movingParts={}
for _,d in moving:GetDescendants() do
 if d:IsA("BasePart") and d.Transparency<0.99 then movingParts[#movingParts+1]=d end
end

local out={movingVisibleParts=#movingParts, radialsFound=#radials, poses={}}
local ok, err = pcall(function()
 for _,d in assembly:GetDescendants() do
  if d:IsA("MeshPart") then
   savedFid[#savedFid+1]={p=d, f=d.CollisionFidelity, q=d.CanQuery}
   d.CollisionFidelity=Enum.CollisionFidelity.PreciseConvexDecomposition
   d.CanQuery=true
  elseif d:IsA("BasePart") then
   savedFid[#savedFid+1]={p=d, f=nil, q=d.CanQuery}
   d.CanQuery=true
  end
 end
 task.wait(3)
 local poseList={
  {n="COLD", g=0,s=0,r=0},
  {n="GATE", g=1,s=0,r=0},
  {n="HALF", g=1,s=0.5,r=0},
  {n="FULL", g=1,s=1,r=0},
  {n="FULL_R18", g=1,s=1,r=math.rad(18)},
  {n="COLD_R36", g=0,s=0,r=math.rad(36)},
 }
 for _,pose in poseList do
  applyPose(pose.g, pose.s, pose.r)
  task.wait(0.2)
  local byPair={} local examples={} local partPairs=0
  for i,p in movingParts do
   local tm=topModel(p)
   local op=OverlapParams.new()
   op.FilterType=Enum.RaycastFilterType.Exclude
   op.FilterDescendantsInstances={tm}
   op.MaxParts=64
   local hits=WS:GetPartsInPart(p, op)
   for _,hh in hits do
    if hh.Transparency<0.99 then
     local g1, g2 = gName(p), gName(hh)
     if g1~=g2 then
      partPairs+=1
      local key = g1<g2 and (g1.." <> "..g2) or (g2.." <> "..g1)
      byPair[key]=(byPair[key] or 0)+1
      if #examples<16 then examples[#examples+1]=p.Name.." <> "..hh.Name end
     end
    end
   end
   if i%40==0 then task.wait() end
  end
  local pairList={}
  for k,v in pairs(byPair) do pairList[#pairList+1]={pair=k, n=v} end
  table.sort(pairList, function(a,b) return a.n>b.n end)
  out.poses[#out.poses+1]={pose=pose.n, partPairs=partPairs, topPairs=pairList, examples=examples}
 end
end)
-- RESTORE (her durumda)
pcall(restorePose)
for _,s in savedFid do
 if s.f then s.p.CollisionFidelity=s.f end
 s.p.CanQuery=s.q
end
out.ok=ok
out.err=err and tostring(err) or nil
return H:JSONEncode(out)
