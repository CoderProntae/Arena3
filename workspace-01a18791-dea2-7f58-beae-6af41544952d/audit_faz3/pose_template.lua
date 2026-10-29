local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local Players=game:GetService("Players")
local world=WS:WaitForChild("CORE_PROTOCOL_V2_WORLD")
assert(world:GetAttribute("ReactorMode")=="COLD", "mod COLD degil")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local moving=assembly:WaitForChild("MOVING")
local staticRoot=assembly:WaitForChild("STATIC")
local GATE=__GATE__ local STROKE=__STROKE__
local sites={
 {tag="UPPER", axis=Vector3.new(0,1,0)},
 {tag="LEFT", axis=Vector3.new(-1,0,0), hatch=1},
 {tag="RIGHT", axis=Vector3.new(1,0,0), hatch=-1},
 {tag="LOWER_LEFT", axis=Vector3.new(-0.72,-0.694,0).Unit},
 {tag="LOWER_RIGHT", axis=Vector3.new(0.72,-0.694,0).Unit},
 {tag="LOWER", axis=Vector3.new(0,-1,0)},
}
local function M(parent,name)
 local it=parent:FindFirstChild(name); assert(it and it:IsA("Model"), "yok "..name)
 return {item=it, at=it:GetPivot()}
end
local rigs={} local topGroup={}
for _,s in sites do
 local head=M(moving,"REACTOR_EMITTER_REV03_"..s.tag)
 local motor=moving:FindFirstChild("REACTOR_PISTON_GUIDE_01_"..s.tag)
 local st={}
 for _,pc in ipairs({"STAGE1","STAGE2","STAGE3","PUSHER"}) do st[pc]=M(motor,pc) end
 local doors=nil
 if s.hatch then local hm=M(moving,"REACTOR_WALL_HATCH_THROUGH_01_"..s.tag); doors={a=M(hm.item,"LEAF_LEFT"), b=M(hm.item,"LEAF_RIGHT")} topGroup[hm.item]="SITE."..s.tag end
 topGroup[head.item]="SITE."..s.tag; topGroup[motor]="SITE."..s.tag
 rigs[#rigs+1]={site=s, head=head, stages=st, doors=doors}
end
local radials={}
for _,ch in moving:GetChildren() do
 if ch:IsA("Model") and ch.Name:find("RADIAL_HATCH") then
  local l=ch:FindFirstChild("LEAF_LEFT") local r=ch:FindFirstChild("LEAF_RIGHT")
  if l and r then radials[#radials+1]={left={item=l,at=l:GetPivot()}, right={item=r,at=r:GetPivot()}} end
 end
end
local function topModel(inst)
 local cur=inst
 while cur and cur.Parent~=moving and cur.Parent~=staticRoot and cur.Parent~=world and cur.Parent~=WS do cur=cur.Parent end
 return cur
end
local function gName(inst)
 local t=topModel(inst); if not t then return "?" end
 if t.Parent==staticRoot then return "STATIC."..t.Name end
 if t.Parent==moving then return topGroup[t] or t.Name end
 if t.Parent==world then return "DUNYA."..t.Name end
 return t.Name
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
end
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local parts={}
for _,d in moving:GetDescendants() do if d:IsA("BasePart") and d.Transparency<0.99 then parts[#parts+1]=d end end
-- POZLA + SENKRON TEST (yield yok)
for _,tag in ipairs({"UPPER","LOWER","LOWER_LEFT","LOWER_RIGHT"}) do assembly:SetAttribute("LiveGate_"..tag, GATE) end
applyPose(GATE, STROKE)
local byPair={} local examples={} local partPairs=0
for _,p in parts do
 local tm=topModel(p)
 local op=OverlapParams.new()
 op.FilterType=Enum.RaycastFilterType.Exclude
 local fl={tm}; for _,c in chars do fl[#fl+1]=c end
 op.FilterDescendantsInstances=fl
 op.MaxParts=48
 local hits=WS:GetPartsInPart(p, op)
 for _,hh in hits do
  if hh.Transparency<0.99 then
   local g1,g2=gName(p),gName(hh)
   if g1~=g2 then
    partPairs+=1
    local key=g1<g2 and (g1.." <> "..g2) or (g2.." <> "..g1)
    byPair[key]=(byPair[key] or 0)+1
    if #examples<14 then examples[#examples+1]=(p.Parent and p.Parent.Name or "?").."/"..p.Name.." <> "..g2.."/"..hh.Name end
   end
  end
 end
end
-- RESTORE
applyPose(0,0)
for _,tag in ipairs({"UPPER","LOWER","LOWER_LEFT","LOWER_RIGHT"}) do assembly:SetAttribute("LiveGate_"..tag, 0) end
local pairList={}
for k,v in pairs(byPair) do pairList[#pairList+1]={pair=k,n=v} end
table.sort(pairList,function(a,b) return a.n>b.n end)
return H:JSONEncode({pose="__NAME__", testedParts=#parts, partPairs=partPairs, topPairs=pairList, examples=examples})
