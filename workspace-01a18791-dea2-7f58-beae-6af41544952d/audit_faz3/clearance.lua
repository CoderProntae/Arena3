local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local Players=game:GetService("Players")
local world=WS:WaitForChild("CORE_PROTOCOL_V2_WORLD")
assert(world:GetAttribute("ReactorMode")=="COLD")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local moving=assembly:WaitForChild("MOVING")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function castClean(o, dir, dist, excl)
 local ex={}
 for _,c in chars do ex[#ex+1]=c end
 for _,c in (excl or {}) do ex[#ex+1]=c end
 for _=1,10 do
  local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances=ex; params.IgnoreWater=true
  local hit=WS:Raycast(o, dir*dist, params)
  if not hit then return nil, nil end
  if hit.Instance:IsA("BasePart") and hit.Instance.Transparency>=0.99 then ex[#ex+1]=hit.Instance
  else return (hit.Position-o).Magnitude, hit.Instance end
 end
 return nil, nil
end
local sites={
 {tag="UPPER", axis=Vector3.new(0,1,0)},
 {tag="LEFT", axis=Vector3.new(-1,0,0), hatch=1},
 {tag="RIGHT", axis=Vector3.new(1,0,0), hatch=-1},
 {tag="LOWER_LEFT", axis=Vector3.new(-0.72,-0.694,0).Unit},
 {tag="LOWER_RIGHT", axis=Vector3.new(0.72,-0.694,0).Unit},
 {tag="LOWER", axis=Vector3.new(0,-1,0)},
}
local function M(parent,name) local it=parent:FindFirstChild(name) return {item=it, at=it:GetPivot()} end
local rigs={}
for _,s in sites do
 local head=M(moving,"REACTOR_EMITTER_REV03_"..s.tag)
 local motor=moving:FindFirstChild("REACTOR_PISTON_GUIDE_01_"..s.tag)
 local st={}
 for _,pc in ipairs({"STAGE1","STAGE2","STAGE3","PUSHER"}) do st[pc]=M(motor,pc) end
 local doors=nil
 if s.hatch then local hm=M(moving,"REACTOR_WALL_HATCH_THROUGH_01_"..s.tag) doors={a=M(hm.item,"LEAF_LEFT"), b=M(hm.item,"LEAF_RIGHT")} end
 rigs[#rigs+1]={site=s, head=head, stages=st, doors=doors, motor=motor}
end
local radials={}
for _,ch in moving:GetChildren() do
 if ch:IsA("Model") and ch.Name:find("RADIAL_HATCH") then
  radials[#radials+1]={left={item=ch:FindFirstChild("LEAF_LEFT"),at=ch:FindFirstChild("LEAF_LEFT"):GetPivot()},right={item=ch:FindFirstChild("LEAF_RIGHT"),at=ch:FindFirstChild("LEAF_RIGHT"):GetPivot()}}
 end
end
local function applyPose(gate, stroke)
 for _,r in rigs do
  local ax=r.site.axis
  r.stages.STAGE1.item:PivotTo(CFrame.new(-ax*(6.6*stroke))*r.stages.STAGE1.at)
  r.stages.STAGE2.item:PivotTo(CFrame.new(-ax*(13.2*stroke))*r.stages.STAGE2.at)
  local push=CFrame.new(-ax*(19.8*stroke))
  r.stages.STAGE3.item:PivotTo(push*r.stages.STAGE3.at)
  r.stages.PUSHER.item:PivotTo(push*r.stages.PUSHER.at)
  r.head.item:PivotTo(push*r.head.at)
  if r.doors then local sl=r.site.hatch*5.85*gate
   r.doors.a.item:PivotTo(CFrame.new(0,0,sl)*r.doors.a.at); r.doors.b.item:PivotTo(CFrame.new(0,0,-sl)*r.doors.b.at) end
 end
 for _,rh in radials do local sl=5.85*gate
  rh.left.item:PivotTo(CFrame.new(0,0,sl)*rh.left.at); rh.right.item:PivotTo(CFrame.new(0,0,-sl)*rh.right.at) end
end
local function ringProbe(center, axis, excl)
 local u = math.abs(axis.Y)>0.9 and Vector3.new(1,0,0) or axis:Cross(Vector3.new(0,1,0)).Unit
 local v = axis:Cross(u).Unit
 local minD, minName, near = 1e9, "", 0
 for i=0,15 do
  local th=i*math.pi/8
  local dir=(u*math.cos(th)+v*math.sin(th))
  local d, inst = castClean(center, dir, 14, excl)
  if d then
   if d<minD then minD=d; minName=inst.Name end
   if d<3.4 then near+=1 end
  end
 end
 return math.floor(minD*100)/100, minName, near
end
local out={poses={}}
for _,pose in ipairs({{n="COLD",g=0,s=0},{n="FULL",g=1,s=1}}) do
 applyPose(pose.g, pose.s)
 local rows={}
 for _,r in rigs do
  local excl={r.head.item, r.motor}
  local hm=moving:FindFirstChild("REACTOR_WALL_HATCH_THROUGH_01_"..r.site.tag)
  if hm then excl[#excl+1]=hm end
  local ext=r.head.item:GetExtentsSize()
  local hp=r.head.item:GetPivot().Position
  local dHead, nHead, nearHead = ringProbe(hp, r.site.axis, excl)
  local sp=r.stages.STAGE2.item:GetPivot().Position
  local dSt, nSt = ringProbe(sp, r.site.axis, excl)
  -- ileri eksenel: kafadan cekirdege (-axis) ilk engel
  local dF, instF = castClean(hp, -r.site.axis, 30, excl)
  rows[#rows+1]={tag=r.site.tag, headExtent={math.floor(ext.X*10)/10,math.floor(ext.Y*10)/10,math.floor(ext.Z*10)/10},
   headRingMin=dHead, headRingHit=nHead, headNear=nearHead, stageRingMin=dSt, stageRingHit=nSt,
   fwdDist=dF and math.floor(dF*100)/100 or -1, fwdHit=instF and instF.Name or "-"}
 end
 out.poses[#out.poses+1]={pose=pose.n, rows=rows}
end
applyPose(0,0)
-- ROTOR radyal bosluk
local rotor=moving:FindFirstChild("REACTOR_REAR_TURBINE_ROTOR")
local center=Vector3.new(0,28.3,-16.25)
local gaps={}
for i=0,35 do
 local th=i*math.pi/18
 local dir=Vector3.new(math.cos(th), math.sin(th), 0)
 local dWall = castClean(center, dir, 16, {rotor})
 -- rotor dahil segment segment
 local pos=center local lastRotor=0 local total=0
 for seg=1,6 do
  local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances=chars; params.IgnoreWater=true
  local hit=WS:Raycast(pos, dir*16, params)
  if not hit then break end
  local dd=(hit.Position-center).Magnitude
  if hit.Instance:IsDescendantOf(rotor) then lastRotor=dd end
  pos=hit.Position+dir*0.05 total=dd
  if not hit.Instance:IsDescendantOf(rotor) and hit.Instance.Transparency<0.99 then break end
 end
 gaps[#gaps+1]={deg=i*10, wall=dWall and math.floor(dWall*100)/100 or -1, rotorLast=math.floor(lastRotor*100)/100,
  gap=(dWall and lastRotor>0) and math.floor((dWall-lastRotor)*100)/100 or -999}
end
out.rotor=gaps
return H:JSONEncode(out)
