-- Add FOUR EXTRA PHYSICAL emitter + telescoping piston assemblies by cloning
-- the already approved GLB imports. The two original side hatches remain as-is.
-- In-source reference silhouette: upper, left, right, lower-left,
-- lower-right, lower (NOT a six-fold evenly spaced radial ring).
-- This one-time Edit-mode assembly does not add beams or simulate controls.
-- The roof, deck and four purpose-made wall/rail service housings remain
-- separate reviewed modeling tasks; these are real mechanisms, not fake mounts.
local H=game:GetService("HttpService")
if game.Name~="AEGIS_Reactor.rbxlx" then error("Wrong Studio place") end
local scene=workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY")
if not scene or not scene:IsA("Model") then error("Existing reviewed meshes not installed") end
if scene:GetAttribute("EmitterModuleCount") then
 error("Already contains additional radial heads. Never run twice.")
end
local moving=scene:FindFirstChild("MOVING")
if not moving or #moving:GetChildren()~=6 then error("Expected exactly original six moving Model roots") end
local emitter=moving:FindFirstChild("REACTOR_EMITTER_REV03_LEFT")
local piston=moving:FindFirstChild("REACTOR_PISTON_GUIDE_01_LEFT")
if not emitter or not piston or not emitter:IsA("Model") or not piston:IsA("Model") then
 error("Approved left-hand GLB mechanism missing")
end
local O=scene:GetAttribute("Origin")
if typeof(O)~="Vector3" or (O-Vector3.new(0,26.5,0)).Magnitude>.02
 or scene:GetAttribute("UnitInStuds")~=1 then
 error("Unexpected scale or origin; stop rather than changing approved geometry")
end
local names={"UPPER","LOWER_LEFT","LOWER_RIGHT","LOWER"}
local outward={Vector3.new(0,1,0),
 Vector3.new(-.72,-.694,0).Unit, Vector3.new(.72,-.694,0).Unit,
 Vector3.new(0,-1,0)}
for _,label in names do
 for _,prefix in {"REACTOR_EMITTER_REV03_","REACTOR_PISTON_GUIDE_01_"} do
  if moving:FindFirstChild(prefix..label) then error("Conflicting root "..prefix..label) end
 end
end
-- Original LEFT emitter +X points INWARDS. Rotate about the true central
-- 3D core, not around the import model's (arbitrary) original Studio pivot.
local created={};local result={}
local ok,why=pcall(function()
 for i,label in names do
  local direction=outward[i]
  local inward=-direction
  local theta=math.atan2(inward.Y,inward.X)
  local rotate=CFrame.new(O)*CFrame.Angles(0,0,theta)*CFrame.new(-O)
  local pair={}
  for _,spec in {{emitter,"REACTOR_EMITTER_REV03_"},
                  {piston,"REACTOR_PISTON_GUIDE_01_"}} do
   local model=spec[1]:Clone()
   model.Name=spec[2]..label
   model:SetAttribute("RadialLabel",label)
   model:SetAttribute("R5EmitterIndex",({UPPER=1,LOWER_LEFT=4,
      LOWER_RIGHT=5,LOWER=6})[label])
   model.Parent=moving
   model:PivotTo(rotate*spec[1]:GetPivot())
   table.insert(created,model)
   pair[#pair+1]=model
  end
  local optic=pair[1]:FindFirstChild("OPTIC__cyan",true)
  local stage=pair[2]:FindFirstChild("STAGE3")
  if not optic or not optic:IsA("MeshPart") or not stage or not stage:IsA("Model") then
   error("Incomplete imported GLB for "..label)
  end
  local radius=(optic.Position-O):Dot(direction)
  if radius<25 or radius>30 then error("Unexpected retracted head projection: "..label.." "..radius) end
  result[label]={radius=math.floor(radius*100)/100,
    nozzle={optic.Position.X,optic.Position.Y,optic.Position.Z},
    emitterMeshes=33,pistonMeshes=20}
 end
 if #moving:GetChildren()~=14 then error("Expected 14 moving Model roots after four clones") end
 scene:SetAttribute("EmitterModuleCount",6)
 scene:SetAttribute("RadialModuleStatus","COLD / four roof-deck service bays pending")
end)
if not ok then
 for _,m in created do if m.Parent then m:Destroy() end end
 error("Four radial head placement aborted and rolled back: "..tostring(why))
end
return H:JSONEncode({success=true,distinctImportedGLBs=scene:GetAttribute("ImportedAssetCount"),
 totalPhysicalEmitters=scene:GetAttribute("EmitterModuleCount"),radialHeadDetails=result,
 note="Four real cloned approved GLB head/piston pairs. No orphan VFX. Top/deck/housings remain unfinished."})
