local WS=game:GetService("Workspace")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local moving=assembly:WaitForChild("MOVING")
local items={}
local function add(it) if it then items[#items+1]=it end end
local sites={
 {tag="UPPER", axis=Vector3.new(0,1,0)},
 {tag="LEFT", axis=Vector3.new(-1,0,0), hatch=1},
 {tag="RIGHT", axis=Vector3.new(1,0,0), hatch=-1},
 {tag="LOWER_LEFT", axis=Vector3.new(-0.72,-0.694,0).Unit},
 {tag="LOWER_RIGHT", axis=Vector3.new(0.72,-0.694,0).Unit},
 {tag="LOWER", axis=Vector3.new(0,-1,0)},
}
local function getPath(inst)
 local parts={} local cur=inst
 while cur and cur~=moving do table.insert(parts,1,cur.Name) cur=cur.Parent end
 return table.concat(parts,"/")
end
local rigs={}
for _,s in sites do
 local head=moving:FindFirstChild("REACTOR_EMITTER_REV03_"..s.tag)
 local motor=moving:FindFirstChild("REACTOR_PISTON_GUIDE_01_"..s.tag)
 local st={}
 for _,pc in ipairs({"STAGE1","STAGE2","STAGE3","PUSHER"}) do st[pc]=motor:FindFirstChild(pc) add(st[pc]) end
 add(head)
 local doors=nil
 if s.hatch then local hm=moving:FindFirstChild("REACTOR_WALL_HATCH_THROUGH_01_"..s.tag)
  doors={a=hm:FindFirstChild("LEAF_LEFT"), b=hm:FindFirstChild("LEAF_RIGHT")}; add(doors.a); add(doors.b) end
 rigs[#rigs+1]={site=s, head=head, stages=st, doors=doors}
end
local radials={}
for _,ch in moving:GetChildren() do
 if ch:IsA("Model") and ch.Name:find("RADIAL_HATCH") then
  local l=ch:FindFirstChild("LEAF_LEFT") local r=ch:FindFirstChild("LEAF_RIGHT")
  add(l); add(r); radials[#radials+1]={l=l,r=r}
 end
end
-- ev pivotlarini kaydet
for i,it in items do
 local comps={it:GetPivot():GetComponents()}
 assembly:SetAttribute("AUDHOME_"..i, getPath(it).."|"..table.concat(comps,","))
end
assembly:SetAttribute("AUDHOME_N", #items)
-- FULL poz
for _,r in rigs do
 local ax=r.site.axis
 local st=r.stages
 local function pv(m,off) return CFrame.new(off)*m:GetPivot() end
end
-- once evleri tablola
local home={}
for _,it in items do home[it]=it:GetPivot() end
for _,r in rigs do
 local ax=r.site.axis
 r.stages.STAGE1:PivotTo(CFrame.new(-ax*6.6)*home[r.stages.STAGE1])
 r.stages.STAGE2:PivotTo(CFrame.new(-ax*13.2)*home[r.stages.STAGE2])
 local push=CFrame.new(-ax*19.8)
 r.stages.STAGE3:PivotTo(push*home[r.stages.STAGE3])
 r.stages.PUSHER:PivotTo(push*home[r.stages.PUSHER])
 r.head:PivotTo(push*home[r.head])
 if r.doors then local sl=r.site.hatch*5.85
  r.doors.a:PivotTo(CFrame.new(0,0,sl)*home[r.doors.a]); r.doors.b:PivotTo(CFrame.new(0,0,-sl)*home[r.doors.b]) end
end
for _,rh in radials do
 rh.l:PivotTo(CFrame.new(0,0,5.85)*home[rh.l]); rh.r:PivotTo(CFrame.new(0,0,-5.85)*home[rh.r])
end
for _,tag in ipairs({"UPPER","LOWER","LOWER_LEFT","LOWER_RIGHT"}) do assembly:SetAttribute("LiveGate_"..tag, 1) end
return "FULL poz tutuldu, ev kaydi="..#items
