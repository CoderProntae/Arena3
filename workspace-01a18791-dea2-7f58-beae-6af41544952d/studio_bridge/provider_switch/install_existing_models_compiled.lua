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
local materials=H:JSONDecode([==[{"REACTOR_EMITTER_REV03":{"TAIL__bronze":{"rgb":[70,32,31],"alpha":1.0,"metal":0.6,"texture":false,"emissive":0.0},"TAIL__obsidian":{"rgb":[15,19,24],"alpha":1.0,"metal":0.67,"texture":false,"emissive":0.0},"TAIL__soot":{"rgb":[6,9,12],"alpha":1.0,"metal":0.32,"texture":false,"emissive":0.0},"TAIL__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"TAIL__pink":{"rgb":[187,45,105],"alpha":1.0,"metal":0.23,"texture":false,"emissive":0.38},"WINDOW__silver":{"rgb":[165,173,179],"alpha":1.0,"metal":0.76,"texture":false,"emissive":0.0},"WINDOW__cyan_core":{"rgb":[16,85,128],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.22},"WINDOW__cyan_shell":{"rgb":[17,85,126],"alpha":0.2196,"metal":0.07,"texture":false,"emissive":0.095},"WINDOW__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"WINDOW__pink":{"rgb":[187,45,105],"alpha":1.0,"metal":0.23,"texture":false,"emissive":0.38},"BODY__body":{"rgb":[36,42,47],"alpha":1.0,"metal":0.71,"texture":false,"emissive":0.0},"BODY__slate":{"rgb":[47,53,61],"alpha":1.0,"metal":0.69,"texture":false,"emissive":0.0},"BODY__obsidian":{"rgb":[15,19,24],"alpha":1.0,"metal":0.67,"texture":false,"emissive":0.0},"BODY__soot":{"rgb":[6,9,12],"alpha":1.0,"metal":0.32,"texture":false,"emissive":0.0},"BODY__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"HEAD__slate":{"rgb":[47,53,61],"alpha":1.0,"metal":0.69,"texture":false,"emissive":0.0},"HEAD__silver":{"rgb":[165,173,179],"alpha":1.0,"metal":0.76,"texture":false,"emissive":0.0},"HEAD__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"HEAD__violet":{"rgb":[86,43,143],"alpha":1.0,"metal":0.19,"texture":false,"emissive":0.31},"HEAD__amber":{"rgb":[191,55,30],"alpha":1.0,"metal":0.39,"texture":false,"emissive":0.38},"HEAD__body":{"rgb":[36,42,47],"alpha":1.0,"metal":0.71,"texture":false,"emissive":0.0},"NOZZLE__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"NOZZLE__body":{"rgb":[36,42,47],"alpha":1.0,"metal":0.71,"texture":false,"emissive":0.0},"NOZZLE__soot":{"rgb":[6,9,12],"alpha":1.0,"metal":0.32,"texture":false,"emissive":0.0},"NOZZLE__silver":{"rgb":[165,173,179],"alpha":1.0,"metal":0.76,"texture":false,"emissive":0.0},"NOZZLE__pink":{"rgb":[187,45,105],"alpha":1.0,"metal":0.23,"texture":false,"emissive":0.38},"NOZZLE__white":{"rgb":[198,208,217],"alpha":1.0,"metal":0.1,"texture":false,"emissive":0.83},"NOZZLE__cyan":{"rgb":[23,167,218],"alpha":1.0,"metal":0.06,"texture":false,"emissive":0.86},"OPTIC__cyan":{"rgb":[23,167,218],"alpha":1.0,"metal":0.06,"texture":false,"emissive":0.86},"ANTENNA__body":{"rgb":[36,42,47],"alpha":1.0,"metal":0.71,"texture":false,"emissive":0.0},"ANTENNA__polished":{"rgb":[115,124,134],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0.0},"ANTENNA__silver":{"rgb":[165,173,179],"alpha":1.0,"metal":0.76,"texture":false,"emissive":0.0},"ANTENNA__soot":{"rgb":[6,9,12],"alpha":1.0,"metal":0.32,"texture":false,"emissive":0.0}},"REACTOR_CORE_MANYETIK_01":{"CENTER__WHITE_CORE":{"rgb":[253,246,255],"alpha":1.0,"metal":0.03,"texture":false,"emissive":1.0},"CENTER__FUCHSIA_CORE":{"rgb":[205,58,162],"alpha":0.2118,"metal":0.03,"texture":false,"emissive":0.72},"CENTER__VIOLET_VAPOR":{"rgb":[61,26,134],"alpha":0.1294,"metal":0.03,"texture":false,"emissive":0.32},"LEFT__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"LEFT__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"LEFT__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"LEFT__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"RIGHT__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"RIGHT__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"RIGHT__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"RIGHT__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"TOP__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"TOP__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"TOP__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"TOP__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"BOTTOM__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"BOTTOM__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"BOTTOM__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"BOTTOM__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"LOWER_LEFT__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"LOWER_LEFT__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"LOWER_LEFT__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"LOWER_LEFT__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"LOWER_RIGHT__BLUE_RAY":{"rgb":[30,39,123],"alpha":0.0784,"metal":0.03,"texture":false,"emissive":0.21},"LOWER_RIGHT__PINK_RAY":{"rgb":[129,39,131],"alpha":0.1098,"metal":0.03,"texture":false,"emissive":0.34},"LOWER_RIGHT__WHITE_GLOW":{"rgb":[103,159,249],"alpha":0.1412,"metal":0.03,"texture":false,"emissive":0.81},"LOWER_RIGHT__WHITE_RAY":{"rgb":[220,233,250],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.98},"LEFT__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"RIGHT__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"TOP__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"BOTTOM__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"LOWER_LEFT__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"LOWER_RIGHT__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"ORBIT_A__ORBIT_COPPER":{"rgb":[201,66,92],"alpha":0.8196,"metal":0.03,"texture":false,"emissive":0.57},"ORBIT_A__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"ORBIT_B__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"ORBIT_B__ORBIT_COPPER":{"rgb":[201,66,92],"alpha":0.8196,"metal":0.03,"texture":false,"emissive":0.57},"ORBIT_C__ORBIT_COPPER":{"rgb":[201,66,92],"alpha":0.8196,"metal":0.03,"texture":false,"emissive":0.57},"ORBIT_C__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"ARCS__ORBIT_HOT":{"rgb":[238,112,180],"alpha":0.9294,"metal":0.03,"texture":false,"emissive":0.84},"SPARKS__SPARK":{"rgb":[249,193,205],"alpha":1.0,"metal":0.03,"texture":false,"emissive":0.81}},"REACTOR_WALL_HATCH_THROUGH_01":{"FACILITY_SHEET__upper":{"rgb":[255,255,255],"alpha":1.0,"metal":0.48,"texture":true,"emissive":0.0},"FACILITY_SHEET__wall":{"rgb":[255,255,255],"alpha":1.0,"metal":0.64,"texture":true,"emissive":0.0},"FACILITY_SHEET__lower":{"rgb":[255,255,255],"alpha":1.0,"metal":0.69,"texture":true,"emissive":0.0},"INSET_SHEET__panel":{"rgb":[255,255,255],"alpha":1.0,"metal":0.84,"texture":true,"emissive":0.0},"WELD_SEAMS__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"EQUIPMENT_LABEL__label":{"rgb":[255,255,255],"alpha":1.0,"metal":0.2,"texture":true,"emissive":0.0},"WARNING_BAND__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"WARNING_PAINT__hazard":{"rgb":[185,78,36],"alpha":1.0,"metal":0.18,"texture":false,"emissive":0.0},"FEED_INNER_WALL__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"FEED_TRIM__edge":{"rgb":[82,77,80],"alpha":1.0,"metal":0.7,"texture":false,"emissive":0.0},"JOINT_BOLTS__bolt":{"rgb":[117,108,105],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"WALL_SHEET_SEAMS__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"UPPER_RACEWAYS__edge":{"rgb":[82,77,80],"alpha":1.0,"metal":0.7,"texture":false,"emissive":0.0},"HATCH_LEFT__panel":{"rgb":[255,255,255],"alpha":1.0,"metal":0.84,"texture":true,"emissive":0.0},"HATCH_LEFT__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"HATCH_LEFT__edge":{"rgb":[82,77,80],"alpha":1.0,"metal":0.7,"texture":false,"emissive":0.0},"HATCH_LEFT__hazard":{"rgb":[185,78,36],"alpha":1.0,"metal":0.18,"texture":false,"emissive":0.0},"HATCH_RIGHT__panel":{"rgb":[255,255,255],"alpha":1.0,"metal":0.84,"texture":true,"emissive":0.0},"HATCH_RIGHT__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"HATCH_RIGHT__edge":{"rgb":[82,77,80],"alpha":1.0,"metal":0.7,"texture":false,"emissive":0.0},"HATCH_RIGHT__hazard":{"rgb":[185,78,36],"alpha":1.0,"metal":0.18,"texture":false,"emissive":0.0},"HATCH_RAILS__dark":{"rgb":[255,255,255],"alpha":1.0,"metal":0.62,"texture":true,"emissive":0.0},"HATCH_RAILS__edge":{"rgb":[82,77,80],"alpha":1.0,"metal":0.7,"texture":false,"emissive":0.0}},"REACTOR_PISTON_GUIDE_01":{"BASE__housing":{"rgb":[255,255,255],"alpha":1.0,"metal":0.68,"texture":true,"emissive":0},"BASE__frame":{"rgb":[51,58,64],"alpha":1.0,"metal":0.72,"texture":false,"emissive":0},"BASE__bolt":{"rgb":[119,129,132],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0},"BASE__bronze":{"rgb":[151,91,54],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"BASE__black":{"rgb":[9,13,20],"alpha":1.0,"metal":0.25,"texture":false,"emissive":0},"STAGE1__neck":{"rgb":[104,115,122],"alpha":1.0,"metal":0.82,"texture":false,"emissive":0},"STAGE1__bronze":{"rgb":[151,91,54],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"STAGE2__rod":{"rgb":[159,173,180],"alpha":1.0,"metal":0.86,"texture":false,"emissive":0},"STAGE2__black":{"rgb":[9,13,20],"alpha":1.0,"metal":0.25,"texture":false,"emissive":0},"STAGE3__rod":{"rgb":[159,173,180],"alpha":1.0,"metal":0.86,"texture":false,"emissive":0},"STAGE3__bronze":{"rgb":[151,91,54],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"PUSHER__frame":{"rgb":[51,58,64],"alpha":1.0,"metal":0.72,"texture":false,"emissive":0},"PUSHER__bolt":{"rgb":[119,129,132],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0},"PUSHER__neck":{"rgb":[104,115,122],"alpha":1.0,"metal":0.82,"texture":false,"emissive":0},"GUIDE_HOOPS__frame":{"rgb":[51,58,64],"alpha":1.0,"metal":0.72,"texture":false,"emissive":0},"GUIDE_CAGE__housing":{"rgb":[255,255,255],"alpha":1.0,"metal":0.68,"texture":true,"emissive":0},"GUIDE_HOOPS__bolt":{"rgb":[119,129,132],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0},"GUIDE_INTERIOR__black":{"rgb":[9,13,20],"alpha":1.0,"metal":0.25,"texture":false,"emissive":0},"BRACKETS__frame":{"rgb":[51,58,64],"alpha":1.0,"metal":0.72,"texture":false,"emissive":0},"OIL_FEED__bronze":{"rgb":[151,91,54],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0}},"REACTOR_REAR_SERVICE_GRILLES_01":{"REAR_BANK_LEFT__wall":{"rgb":[255,255,255],"alpha":1.0,"metal":0.58,"texture":true,"emissive":0.0},"REAR_BANK_LEFT__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_LEFT__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_1__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_2__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_LEFT_SLOT_3__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_LEFT__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_LEFT__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"REAR_BANK_LEFT__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"REAR_BANK_LEFT__amber":{"rgb":[159,79,43],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"UPPER_GRILLE_LEFT_1__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_1__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"UPPER_GRILLE_LEFT_2__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"UPPER_GRILLE_LEFT_2__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__wall":{"rgb":[255,255,255],"alpha":1.0,"metal":0.58,"texture":true,"emissive":0.0},"REAR_BANK_RIGHT__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_1__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_2__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__blue":{"rgb":[41,88,131],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__slat":{"rgb":[21,43,77],"alpha":1.0,"metal":0.47,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT_SLOT_3__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"REAR_BANK_RIGHT__amber":{"rgb":[159,79,43],"alpha":1.0,"metal":0.3,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_1__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__paint":{"rgb":[255,255,255],"alpha":1.0,"metal":0.76,"texture":true,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__seal":{"rgb":[10,13,19],"alpha":1.0,"metal":0.08,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__recess":{"rgb":[11,19,36],"alpha":1.0,"metal":0.2,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__edge":{"rgb":[114,132,143],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__spine":{"rgb":[61,83,108],"alpha":1.0,"metal":0.64,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__copper":{"rgb":[130,73,52],"alpha":1.0,"metal":0.68,"texture":false,"emissive":0.0},"UPPER_GRILLE_RIGHT_2__steel":{"rgb":[42,51,63],"alpha":1.0,"metal":0.74,"texture":false,"emissive":0.0}},"REACTOR_REAR_BULKHEAD_IRON_REV04":{"REAR_LOAD_BEARING_LINER__lining":{"rgb":[82,66,59],"alpha":1.0,"metal":0.57,"texture":false,"emissive":0},"ROLLED_IRON_COURSE_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"ROLLED_IRON_COURSE_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"ROLLED_IRON_COURSE_3__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"ROLLED_IRON_COURSE_4__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"STAMPED_COURSE_WELDS__oxide":{"rgb":[105,65,51],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"SEAM_FASTENERS__cut":{"rgb":[125,133,136],"alpha":1.0,"metal":0.85,"texture":false,"emissive":0},"OCTAGON_WING_FOLD__cut":{"rgb":[125,133,136],"alpha":1.0,"metal":0.85,"texture":false,"emissive":0},"BENT_EDGE_IRON__rib":{"rgb":[52,57,61],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0},"SERVICE_MARKER_L__rib":{"rgb":[52,57,61],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0},"SERVICE_MARKER_L__oxide":{"rgb":[105,65,51],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"SERVICE_MARKER_L__cut":{"rgb":[125,133,136],"alpha":1.0,"metal":0.85,"texture":false,"emissive":0},"REAR_SAFETY_TABS__orange":{"rgb":[190,93,45],"alpha":1.0,"metal":0.37,"texture":false,"emissive":0},"SERVICE_MARKER_R__rib":{"rgb":[52,57,61],"alpha":1.0,"metal":0.79,"texture":false,"emissive":0},"SERVICE_MARKER_R__oxide":{"rgb":[105,65,51],"alpha":1.0,"metal":0.75,"texture":false,"emissive":0},"SERVICE_MARKER_R__cut":{"rgb":[125,133,136],"alpha":1.0,"metal":0.85,"texture":false,"emissive":0}},"REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02":{"LEFT_STRUCTURAL_WAIST_TRUE_PORT__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"LEFT_STAMPED_WAIST_COURSE_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_STAMPED_WAIST_COURSE_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_STAMPED_WAIST_COURSE_3__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_LOWER_DIAGONAL_STRUCTURAL_BLOCK__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"LEFT_LOWER_SLOPED_ROLLED_IRON_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_LOWER_SLOPED_ROLLED_IRON_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_LOWER_FRONT_DIAGONAL_CORNER_GUSSET__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"LEFT_LOWER_FRONT_DIAGONAL_CORNER_GUSSET__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"LEFT_UPPER_DIAGONAL_STRUCTURAL_BLOCK__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"LEFT_UPPER_SLOPED_ROLLED_IRON_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_UPPER_SLOPED_ROLLED_IRON_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"LEFT_UPPER_FRONT_DIAGONAL_CORNER_GUSSET__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"LEFT_UPPER_FRONT_DIAGONAL_CORNER_GUSSET__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"LEFT_HATCH_STEEL_INTERFACE__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"LEFT_RECESSED_METAL_SLIDER_POCKET__pocket":{"rgb":[85,89,91],"alpha":1.0,"metal":0.84,"texture":false,"emissive":0},"LEFT_CORNER_WARNING__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"LEFT_CORNER_WARNING__red":{"rgb":[137,48,34],"alpha":1.0,"metal":0.56,"texture":false,"emissive":0},"LEFT_CORNER_WARNING__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"LEFT_FRONT_WINDOW_FUTURE_JOINT__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"RIGHT_STRUCTURAL_WAIST_TRUE_PORT__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"RIGHT_STAMPED_WAIST_COURSE_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_STAMPED_WAIST_COURSE_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_STAMPED_WAIST_COURSE_3__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_LOWER_DIAGONAL_STRUCTURAL_BLOCK__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"RIGHT_LOWER_SLOPED_ROLLED_IRON_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_LOWER_SLOPED_ROLLED_IRON_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_LOWER_FRONT_DIAGONAL_CORNER_GUSSET__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"RIGHT_LOWER_FRONT_DIAGONAL_CORNER_GUSSET__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"RIGHT_UPPER_DIAGONAL_STRUCTURAL_BLOCK__liner":{"rgb":[65,66,68],"alpha":1.0,"metal":0.77,"texture":false,"emissive":0},"RIGHT_UPPER_SLOPED_ROLLED_IRON_1__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_UPPER_SLOPED_ROLLED_IRON_2__iron":{"rgb":[255,255,255],"alpha":1.0,"metal":1.0,"texture":true,"emissive":0},"RIGHT_UPPER_FRONT_DIAGONAL_CORNER_GUSSET__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"RIGHT_UPPER_FRONT_DIAGONAL_CORNER_GUSSET__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"RIGHT_HATCH_STEEL_INTERFACE__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"RIGHT_RECESSED_METAL_SLIDER_POCKET__pocket":{"rgb":[85,89,91],"alpha":1.0,"metal":0.84,"texture":false,"emissive":0},"RIGHT_CORNER_WARNING__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0},"RIGHT_CORNER_WARNING__red":{"rgb":[137,48,34],"alpha":1.0,"metal":0.56,"texture":false,"emissive":0},"RIGHT_CORNER_WARNING__edge":{"rgb":[142,148,148],"alpha":1.0,"metal":0.92,"texture":false,"emissive":0},"RIGHT_FRONT_WINDOW_FUTURE_JOINT__frame":{"rgb":[61,66,70],"alpha":1.0,"metal":0.88,"texture":false,"emissive":0}}}]==])
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
