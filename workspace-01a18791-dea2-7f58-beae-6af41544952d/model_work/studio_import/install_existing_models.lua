-- ONE-TIME EDIT-MODE INSTALLER for seven user-reviewed GLBs. Not runtime script.
-- Scope: backup imported roots, correct Roblox import's observed 180-degree
-- X/Z orientation, restore approved material colors, align original geometry
-- at one 1-source-unit = 1-stud basis, and prepare grouped moving assemblies.
-- No mouse calls, play-state changes, arbitrary world removal, or audio claim.
-- If a preflight or QA assertion fails, the original imports are restored.
local names={
 "REACTOR_EMITTER_REV03","REACTOR_CORE_MANYETIK_01",
 "REACTOR_WALL_HATCH_THROUGH_01","REACTOR_PISTON_GUIDE_01",
 "REACTOR_REAR_SERVICE_GRILLES_01","REACTOR_REAR_BULKHEAD_IRON_REV04",
 "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02",
}
local offsets={
 -- expected converted GLB bounding-centers measured from original vertices
 REACTOR_EMITTER_REV03=Vector3.new(.0915,0,0),
 REACTOR_CORE_MANYETIK_01=Vector3.new(0,0,-.287),
 REACTOR_WALL_HATCH_THROUGH_01=Vector3.new(-1.44,0,0),
 REACTOR_PISTON_GUIDE_01=Vector3.new(-18.145,0,0),
 REACTOR_REAR_SERVICE_GRILLES_01=Vector3.new(0,4.985,-14.117),
 REACTOR_REAR_BULKHEAD_IRON_REV04=Vector3.new(0,0,-14.253),
 REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02=Vector3.new(0,0,1.356),
}
local extents={
 REACTOR_EMITTER_REV03=Vector3.new(18.483,6.140,6.140),
 REACTOR_CORE_MANYETIK_01=Vector3.new(14.720,14.720,11.234),
 REACTOR_WALL_HATCH_THROUGH_01=Vector3.new(3.560,20.500,23.740),
 REACTOR_PISTON_GUIDE_01=Vector3.new(31.310,8.664,8.664),
 REACTOR_REAR_SERVICE_GRILLES_01=Vector3.new(31.740,23.750,2.185),
 REACTOR_REAR_BULKHEAD_IRON_REV04=Vector3.new(49.192,43.192,3.735),
 REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02=Vector3.new(55.440,43.286,33.523),
}
local counts={33,41,23,20,78,16,40}
local ORIGIN=Vector3.new(0,26.50,0)  -- old R5 reactor's world-space center
local ROT180=CFrame.Angles(0,math.pi,0)
local HATCH_AXIS_X=24.5
local HATCH_DEPTH_Z=2.70
local RETRACTED_X=-11.47
local S=game:GetService("ServerStorage")
local H=game:GetService("HttpService")
if game.Name~="AEGIS_Reactor.rbxlx" then error("Unexpected place: "..game.Name) end
if workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY") then
 error("Assembly already exists. Do not run installer twice.")
end
if S:FindFirstChild("REACTOR_IMPORT_BACKUP_2026_10_25") then
 error("Import backup already exists; inspect it before attempting another install.")
end
local inputs={}
for i,n in names do
 local model=workspace:FindFirstChild(n)
 if not model or not model:IsA("Model") or model.Parent~=workspace then
  error("Missing imported Model directly in Workspace: "..n)
 end
 local c=0
 for _,d in model:GetDescendants() do if d:IsA("MeshPart") then c+=1 end end
 if c~=counts[i] then error(n.." unexpected MeshPart count "..c) end
 local _,size=model:GetBoundingBox()
 local want=extents[n]
 local rat={size.X/want.X,size.Y/want.Y,size.Z/want.Z}
 if n=="REACTOR_REAR_SERVICE_GRILLES_01" then
  -- Live import audit: every individual grille mesh retains its source size,
  -- but both 39-node banks were moved ~1.29 studs toward the centre. Whole
  -- X width is thus misleading; only Y/Z carry the UNIFORM scale factor.
  if math.abs(rat[2]-rat[3])>.004 or rat[2]<1.14 or rat[2]>1.17
      or rat[1]<1.04 or rat[1]>1.17 then
   error("Grille dimensions outside the audited scale/spacing envelope")
  end
 else
  for axis=1,3 do
   if math.abs(rat[axis]-1)>.004 then error(n.." import scale mismatch "..axis) end
  end
 end
 inputs[n]=model
end
local materials=H:JSONDecode([==[__MATERIAL_JSON__]==])
local function tint(m,source_name)
 local map=materials[source_name]
 local seen=0
 for _,p in m:GetDescendants() do
  if p:IsA("MeshPart") then
   seen+=1
   local meta=map[p.Name]
   if not meta then error("Missing approved material for "..source_name.."/"..p.Name) end
   p.Anchored=true; p.CanCollide=false; p.CanTouch=false
   if meta.texture and p:FindFirstChildOfClass("SurfaceAppearance") then
    p.Color=Color3.new(1,1,1) -- keep the imported PBR maps un-tinted
    p.Material=Enum.Material.Plastic
   else
    p.Color=Color3.fromRGB(meta.rgb[1],meta.rgb[2],meta.rgb[3])
    p.Material=(meta.metal>=.45) and Enum.Material.Metal or Enum.Material.SmoothPlastic
    p.Reflectance=(meta.metal>=.65) and .025 or 0
   end
   p.Transparency=1-meta.alpha
   p:SetAttribute("GLB_VisibleTransparency",p.Transparency)
   if source_name=="REACTOR_CORE_MANYETIK_01" then
    p.Transparency=1 -- no active star/rays/plasma in COLD
    p.CanQuery=false
    p.CastShadow=false
   elseif meta.alpha<.4 then p.CastShadow=false end
  end
 end
 if seen<1 then error("empty source") end
end
local function centre_correct(m,name)
 if name=="REACTOR_REAR_SERVICE_GRILLES_01" then
  local _,size=m:GetBoundingBox()
  m:ScaleTo(m:GetScale()*(extents[name].Y/size.Y))
 end
 local c=m:GetBoundingBox()
 local desired=ORIGIN+offsets[name]
 local pivot=m:GetPivot()
 -- Actual import inspection: node RIGHT showed up on the LEFT, and front
 -- hatch leaf on the BACK. The importer did a 180-degree Y rotation. Apply
 -- one matching proper rotation to restore right/front before positioning.
 m:PivotTo(CFrame.new(desired)*ROT180*CFrame.new(-c.Position)*pivot)
 if name=="REACTOR_REAR_SERVICE_GRILLES_01" then
  -- Source bank centers are X=-10.75/+10.75. The live Importer preserved
  -- each individual node's geometry but shifted the 39 left/right nodes
  -- toward one another. Move their EXISTING nodes back outward; never
  -- stretch their approved three openings or substitute visual Parts.
  local left=m:FindFirstChild("REAR_BANK_LEFT__wall",true)
  local right=m:FindFirstChild("REAR_BANK_RIGHT__wall",true)
  if not left or not right then error("Grille bank landmarks missing") end
  local corrections={LEFT=-10.75-left.Position.X,RIGHT=10.75-right.Position.X}
  if math.abs(corrections.LEFT)>3 or math.abs(corrections.RIGHT)>3 then
   error("Grille bank positions too far from source")
  end
  for _,node in m:GetChildren() do
   if node:IsA("Model") then
    local side=node.Name:find("LEFT",1,true) and "LEFT"
      or (node.Name:find("RIGHT",1,true) and "RIGHT")
    if not side then error("Unexpected unassigned grille node "..node.Name) end
    node:PivotTo(CFrame.new(corrections[side],0,0)*node:GetPivot())
   end
  end
 end
 local after,asize=m:GetBoundingBox()
 if (after.Position-desired).Magnitude>.06 then
  error(name.." center not preserved during axis/spacing correction")
 end
 local want=extents[name]
 if (asize-want).Magnitude>.14 then
  error(name.." extents after correction: "..tostring(asize).." vs "..tostring(want))
 end
end
local function asset_under(parent,m,newname)
 m.Name=newname;m.Parent=parent
 m:SetAttribute("ReactorSource",newname)
end
local function pose(pivot,dx,rotation)
 local origin=CFrame.new(ORIGIN)
 local t=origin*CFrame.new(dx,0,HATCH_DEPTH_Z)*rotation*origin:Inverse()
 return t*pivot
end
local function group_motion(m,prefixes)
 for _,pair in prefixes do
  local label,prefix=pair[1],pair[2]
  local group=Instance.new("Model")
  group.Name=label
  group.Parent=m
  local total=0
  for _,child in m:GetChildren() do
   if child~=group and child:IsA("Model") and child.Name:sub(1,#prefix)==prefix then
    child.Parent=group;total+=1
   end
  end
  if total<1 then error(m.Name.." has no motion group "..prefix) end
  group:SetAttribute("SourceNodes",total)
 end
end
local function qa_side(assembly)
 local m=assembly.STATIC:FindFirstChild("REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02")
 local l=m:FindFirstChild("LEFT_CORNER_WARNING__frame",true)
 local r=m:FindFirstChild("RIGHT_UPPER_FRONT_DIAGONAL_CORNER_GUSSET__frame",true)
 if not l or not r or not l:IsA("MeshPart") or not r:IsA("MeshPart") then
  error("Side-wall orientation QA nodes unavailable")
 end
 if l.Position.X>=-18 or r.Position.X<=18 then
  error("Side-wall LEFT/RIGHT geometry is still swapped")
 end
 local rearg=assembly.STATIC:FindFirstChild("REACTOR_REAR_SERVICE_GRILLES_01")
 local right=rearg:FindFirstChild("REAR_BANK_RIGHT__wall",true)
 if not right or right.Position.X<0 then error("Rear grilles LEFT/RIGHT mismatch") end
end
-- Preflight passed. Keep a reversible copy of the seven imported roots.
local backup=Instance.new("Folder")
backup.Name="REACTOR_IMPORT_BACKUP_2026_10_25"
backup.Parent=S
for _,n in names do
 local copy=inputs[n]:Clone()
 copy.Parent=backup
 task.wait()
end
local ok,result=pcall(function()
 local scene=Instance.new("Model")
 scene.Name="REACTOR_MESH_ASSEMBLY";scene.Parent=workspace
 scene:SetAttribute("ImportedAssetCount",7)
 scene:SetAttribute("UnitInStuds",1)
 scene:SetAttribute("Origin",ORIGIN)
 scene:SetAttribute("MotionStatus","COLD")
 local fixed=Instance.new("Model");fixed.Name="STATIC";fixed.Parent=scene
 local moving=Instance.new("Model");moving.Name="MOVING";moving.Parent=scene
 for _,n in names do
  local m=inputs[n]
  tint(m,n)
  centre_correct(m,n)
  if n=="REACTOR_EMITTER_REV03" or n=="REACTOR_WALL_HATCH_THROUGH_01"
      or n=="REACTOR_PISTON_GUIDE_01" then
   local neutral=m:GetPivot()
   local right=m:Clone()
   local ex=(n=="REACTOR_EMITTER_REV03") and RETRACTED_X or 0
   local ldx=-HATCH_AXIS_X+ex
   local rdx=HATCH_AXIS_X-ex
   m:PivotTo(pose(neutral,ldx,CFrame.new()))
   right:PivotTo(pose(neutral,rdx,ROT180))
   asset_under(moving,m,n.."_LEFT")
   asset_under(moving,right,n.."_RIGHT")
   if n=="REACTOR_WALL_HATCH_THROUGH_01" then
    for _,h in {m,right} do
     group_motion(h,{{"LEAF_LEFT","HATCH_LEFT"},{"LEAF_RIGHT","HATCH_RIGHT"}})
    end
   elseif n=="REACTOR_PISTON_GUIDE_01" then
    for _,p in {m,right} do
     group_motion(p,{{"STAGE1","STAGE1"},{"STAGE2","STAGE2"},
                    {"STAGE3","STAGE3"},{"PUSHER","PUSHER"}})
    end
   end
  else
   asset_under(fixed,m,n)
  end
  task.wait() -- yields per imported component; never freeze an entire room
 end
 qa_side(scene)
 return scene
end)
if not ok then
 local scene=workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY")
 if scene then scene:Destroy() end
 for _,n in names do
  local root=workspace:FindFirstChild(n)
  if root and root:IsA("Model") then root:Destroy() end
 end
 for _,saved in backup:GetChildren() do saved:Clone().Parent=workspace end
 backup:Destroy()
 error("INSTALL ABORTED / original seven imported models restored: "..tostring(result))
end
local scene=result
local finalCF,finalSize=scene:GetBoundingBox()
return H:JSONEncode({success=true,assembly=scene.Name,backup=backup.Name,
 scale=scene:GetAttribute("UnitInStuds"),
 static_count=#scene.STATIC:GetChildren(),moving_count=#scene.MOVING:GetChildren(),
 bounds={centre={finalCF.Position.X,finalCF.Position.Y,finalCF.Position.Z},
         size={finalSize.X,finalSize.Y,finalSize.Z}},
 note="COLD: rays hidden; doors and piston grouped but no running animation yet"})
