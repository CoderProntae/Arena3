-- Gameplay mesh controller: non-startup motion, damage and ONLINE.
-- CHECKPOINT 01 delegates STARTUP motion to a separate server-only owner.
-- It never manufactures a backup ray while this first visual gate is open.
local RunService=game:GetService("RunService")
local SS=game:GetService("ServerStorage")
local WS=game:GetService("Workspace")
local scene=WS:WaitForChild("REACTOR_MESH_ASSEMBLY",30)
if not scene or not scene:IsA("Model") then
 warn("[MESH] No reviewed reactor assembly; leave R5 alone")
 return
end
local moving=scene:WaitForChild("MOVING",8)
local fixed=scene:WaitForChild("STATIC",8)
if not moving or not fixed then warn("[MESH] Missing GLB groups");return end
if scene:GetAttribute("EmitterModuleCount")~=6 then
 warn("[MESH] Six physical heads are required. Refusing orphan rays.")
 return
end
local core=fixed:FindFirstChild("REACTOR_CORE_MANYETIK_01")
if not core or not core:IsA("Model") then warn("[MESH] Core GLB missing");return end
local world=WS:WaitForChild("CORE_PROTOCOL_V2_WORLD",60)
if not world then warn("[MESH] R5 not running; keeping COLD");return end
-- Retire ONLY the old Part-based projector folder at Play time. R5's room,
-- physical controls, server simulation, emergency scenario all stay in place.
local old=world:FindFirstChild("03_STAR_REACTOR")
if old then old.Parent=SS end
local O=scene:GetAttribute("Origin") or Vector3.new(0,26.5,0)
local sites={
 {tag="UPPER",coreTag="TOP",i=1,out=Vector3.new(0,1,0)},
 {tag="LEFT",coreTag="LEFT",i=2,out=Vector3.new(-1,0,0),side=1},
 {tag="RIGHT",coreTag="RIGHT",i=3,out=Vector3.new(1,0,0),side=-1},
 {tag="LOWER_LEFT",coreTag="LOWER_LEFT",i=4,
  out=Vector3.new(-.72,-.694,0).Unit},
 {tag="LOWER_RIGHT",coreTag="LOWER_RIGHT",i=5,
  out=Vector3.new(.72,-.694,0).Unit},
 {tag="LOWER",coreTag="BOTTOM",i=6,out=Vector3.new(0,-1,0)},
}
local function must(parent,name)
 local m=parent:FindFirstChild(name)
 if not m or not m:IsA("Model") then error("[MESH] Required GLB group missing: "..name) end
 return m
end
local rigs={}
for _,site in sites do
 local tag=site.tag
 local emitter=must(moving,"REACTOR_EMITTER_REV03_"..tag)
 local piston=must(moving,"REACTOR_PISTON_GUIDE_01_"..tag)
 local optic=emitter:FindFirstChild("OPTIC__cyan",true)
 if not optic or not optic:IsA("MeshPart") then
  error("[MESH] Physical photon nozzle missing for "..tag)
 end
 local rig={site=site,emitter=emitter,emitterHome=emitter:GetPivot(),
  optic=optic,piston=piston,stages={},doors={},gate=0,stroke=0,failed=false,
  feedGlow=0,bendParts={},detailParts={}}
 -- Keep the approved dark-blue cell and all four antenna geometries in
 -- COLD. Their MATERIAL/LIGHT state alone changes during prewarming.
 for _,part in emitter:GetDescendants() do
  if part:IsA("MeshPart") and (part.Name=="HEAD__amber"
    or part.Name=="WINDOW__cyan_core" or part.Name=="NOZZLE__white") then
   rig.detailParts[#rig.detailParts+1]={p=part,name=part.Name,
    material=part.Material,color=part.Color,alpha=part.Transparency}
  end
 end
 -- These are approved physically separate MeshParts, not an orange fake
 -- sphere. A ruptured projector twists/buckles its actual nozzle/antenna
 -- metal. Snapshot local poses so reset restores the intact COLD assembly.
 for _,part in emitter:GetDescendants() do
  if part:IsA("MeshPart") and
    (part.Name:sub(1,8)=="NOZZLE__" or part.Name:sub(1,9)=="ANTENNA__") then
   rig.bendParts[#rig.bendParts+1]={part=part,
     localPose=emitter:GetPivot():ToObjectSpace(part.CFrame),
     color=part.Color,material=part.Material,alpha=part.Transparency}
  end
 end
 if #rig.bendParts<3 then error("[MESH] Insufficient real damage zones for "..tag) end
 for _,name in {"STAGE1","STAGE2","STAGE3","PUSHER"} do
  local m=must(piston,name)
  rig.stages[name]={m=m,home=m:GetPivot()}
 end
 if site.side then
  local hatch=must(moving,"REACTOR_WALL_HATCH_THROUGH_01_"..tag)
  for _,name in {"LEAF_LEFT","LEAF_RIGHT"} do
   local m=must(hatch,name)
   rig.doors[name]={m=m,home=m:GetPivot()}
  end
 end
 rigs[site.i]=rig
end
if #rigs~=6 then error("[MESH] No unmodeled laser may exist") end
local anchor=Instance.new("Part")
anchor.Name="MESH_EFFECTS_INVISIBLE_ANCHOR"
anchor.Size=Vector3.new(.12,.12,.12);anchor.CFrame=CFrame.new(O)
anchor.Transparency=1;anchor.Anchored=true;anchor.CanCollide=false
anchor.CanTouch=false;anchor.CanQuery=false;anchor.CastShadow=false
anchor.Parent=scene
local center=Instance.new("Attachment");center.Name="CORE_FOCUS";center.Parent=anchor
local coreLamp=Instance.new("PointLight")
coreLamp.Name="CORE_STATE_LIGHT";coreLamp.Brightness=0;coreLamp.Range=38
coreLamp.Shadows=true;coreLamp.Color=Color3.fromRGB(152,157,255)
coreLamp.Parent=anchor
-- Pale bluish worklights, affixed by Attachments to the existing invisible
-- VFX anchor (no additional Part geometry; APPROVED brown metal unchanged).
-- The reference chamber is readable even when the star is truly OFF.
local worklights={}
for n,at in {Vector3.new(-15,11,10),Vector3.new(15,11,10),
 Vector3.new(-13,-9,9),Vector3.new(13,-9,9)} do
 local a=Instance.new("Attachment");a.Name="CHAMBER_FILL_SOCKET_"..n
 a.Position=at;a.Parent=anchor
 local l=Instance.new("PointLight");l.Name="COLD_WORKLIGHT_"..n
 l.Color=Color3.fromRGB(181,211,243);l.Range=31;l.Brightness=0.85
 l.Shadows=n<=2;l.Parent=a;worklights[n]=l
end
local function particle(name,tex,color,initialSize,endSize)
 local p=Instance.new("ParticleEmitter")
 p.Name=name;p.Texture=tex;p.Enabled=false;p.Rate=0
 p.Color=ColorSequence.new(color);p.LightEmission=.65
 p.Speed=NumberRange.new(.8,3.5);p.Lifetime=NumberRange.new(.2,.8)
 p.SpreadAngle=Vector2.new(155,155)
 p.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,initialSize),
  NumberSequenceKeypoint.new(.4,endSize),NumberSequenceKeypoint.new(1,0)})
 p.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.28),
  NumberSequenceKeypoint.new(.73,.57),NumberSequenceKeypoint.new(1,1)})
 return p
end
local sparks=particle("DYNAMIC_ION_PARTICLES",
 "rbxasset://textures/particles/sparkles_main.dds",
 Color3.fromRGB(154,131,255),.22,1.35)
sparks.Parent=center
local vapor=particle("DYNAMIC_PLASMA_VAPOR",
 "rbxasset://textures/particles/smoke_main.dds",
 Color3.fromRGB(78,61,159),2.4,9.8)
vapor.LightEmission=.24;vapor.Lifetime=NumberRange.new(.8,2.5)
vapor.Speed=NumberRange.new(.25,1.4);vapor.Parent=center
local corona=particle("MOVING_VIOLET_MELTDOWN_CORONA",
 "rbxasset://textures/particles/smoke_main.dds",
 Color3.fromRGB(177,81,246),4.6,13.8)
corona.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.76),
 NumberSequenceKeypoint.new(.6,.89),NumberSequenceKeypoint.new(1,1)})
corona.LightEmission=.63;corona.Speed=NumberRange.new(.2,1.1)
corona.Lifetime=NumberRange.new(.55,1.25);corona.Parent=center
local ignitionCloud=particle("CYAN_IGNITION_VOLUME_NOT_GLASS_DECAL",
 "rbxasset://textures/particles/smoke_main.dds",
 Color3.fromRGB(38,206,255),1.1,12.6)
ignitionCloud.LightEmission=.85
ignitionCloud.Speed=NumberRange.new(1.7,5.1)
ignitionCloud.Lifetime=NumberRange.new(.7,1.7)
ignitionCloud.Transparency=NumberSequence.new({
 NumberSequenceKeypoint.new(0,.35),NumberSequenceKeypoint.new(.5,.62),
 NumberSequenceKeypoint.new(1,1)})
ignitionCloud.Parent=center
local streams={}
for _,rig in rigs do
 local optic=rig.optic
 local tip=Instance.new("Attachment");tip.Name="REAL_NOZZLE_ATTACHMENT"
 tip.Parent=optic;rig.tip=tip
 local halo=Instance.new("Beam")
 halo.Name="BASE_ION_STREAM_"..rig.site.tag
 halo.Attachment0=center;halo.Attachment1=tip
 halo.Segments=14;halo.FaceCamera=true;halo.Width0=.49;halo.Width1=.34
 halo.Color=ColorSequence.new(Color3.fromRGB(64,82,233),
   Color3.fromRGB(74,185,255));halo.LightEmission=.82
 halo.Transparency=NumberSequence.new(1);halo.Enabled=false
 halo.Parent=anchor
 local hot=Instance.new("Beam")
 hot.Name="HEATING_PHOTON_FILAMENT_"..rig.site.tag
 hot.Attachment0=center;hot.Attachment1=tip
 hot.Segments=14;hot.FaceCamera=true;hot.Width0=.13;hot.Width1=.11
 hot.Color=ColorSequence.new(Color3.fromRGB(229,237,255))
 hot.LightEmission=1;hot.Transparency=NumberSequence.new(1)
 hot.Enabled=false;hot.Parent=anchor
 streams[rig.site.i]={halo,hot}
 local lamp=Instance.new("PointLight")
 lamp.Name="PHYSICAL_OPTIC_GLOW";lamp.Color=Color3.fromRGB(61,178,255)
 lamp.Range=11;lamp.Brightness=0;lamp.Parent=optic;rig.lamp=lamp
 local leak=particle("BROKEN_NOZZLE_SMOKE",
  "rbxasset://textures/particles/smoke_main.dds",
  Color3.fromRGB(109,111,126),.45,2.2)
 leak.LightEmission=0;leak.Lifetime=NumberRange.new(.6,1.6)
 leak.Speed=NumberRange.new(1,3.1);leak.Parent=tip;rig.leak=leak
 local shower=particle("METAL_ARC_AT_REAL_HEAD",
  "rbxasset://textures/particles/sparkles_main.dds",
  Color3.fromRGB(255,134,65),.22,.5)
 shower.Speed=NumberRange.new(5,14)
 shower.Lifetime=NumberRange.new(.13,.48)
 shower.Acceleration=Vector3.new(0,-17,0)
 shower.Parent=tip;rig.shower=shower
end
-- Small two-point Trails trace actual moving plasma, not painted GLB rays.
local orbits={}
for i=1,2 do
 local p=Instance.new("Part")
 p.Name="INVISIBLE_ORBIT_TRAIL_"..i
 p.Size=Vector3.new(.12,.12,.12);p.CFrame=CFrame.new(O)
 p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false
 p.CastShadow=false;p.Transparency=1;p.Parent=scene
 local a=Instance.new("Attachment");a.Position=Vector3.new(-.35,0,0);a.Parent=p
 local b=Instance.new("Attachment");b.Position=Vector3.new(.35,0,0);b.Parent=p
 local t=Instance.new("Trail");t.Name="STATE_GATED_VIOLET_ORBIT_"..i
 t.Attachment0=a;t.Attachment1=b;t.Lifetime=.38;t.MinLength=.07
 t.FaceCamera=true;t.LightEmission=.83
 t.Color=ColorSequence.new(Color3.fromRGB(120,84,252),
  Color3.fromRGB(221,68,172))
 t.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.3),
  NumberSequenceKeypoint.new(1,1)})
 t.Enabled=false;t.Parent=p
 orbits[i]={p=p,t=t}
end
-- The source GLB separated TOP, LEFT, RIGHT, LOWER_LEFT, LOWER_RIGHT,
-- BOTTOM into independent real triangle meshes. A feed stays invisible unless
-- its matching approved emitter exists, its R5 relay has fired, and it is
-- physically extended and NOT broken. No more orphan six-way core rays.
local zoneId={TOP=1,LEFT=2,RIGHT=3,LOWER_LEFT=4,
 LOWER_RIGHT=5,BOTTOM=6}
local coreParts={}
for _,p in core:GetDescendants() do
 if p:IsA("MeshPart") then
  local v=p:GetAttribute("GLB_VisibleTransparency")
  local zone=p.Name:match("^(.-)__") or ""
  coreParts[#coreParts+1]={p=p,v=typeof(v)=="number" and v or 0,
   feed=zoneId[zone],zone=zone,size=p.Size,color=p.Color,
   material=p.Material}
  p.Transparency=1;p.Material=Enum.Material.SmoothPlastic
  p.CanQuery=false;p.CastShadow=false
 end
end
local function ease(x)
 x=math.clamp(x,0,1)
 return x*x*(3-2*x)
end
local function toward(x,want,amount)
 if x<want then return math.min(want,x+amount) end
 return math.max(want,x-amount)
end
local function bit(mask,i)
 return (math.floor(mask/2^(i-1))%2)==1
end
local function place(r)
 local displacement=-r.site.out*19.8*ease(r.stroke)
 local cf=CFrame.new(displacement)
 r.stages.STAGE1.m:PivotTo(CFrame.new(-r.site.out*6.6*ease(r.stroke))*r.stages.STAGE1.home)
 r.stages.STAGE2.m:PivotTo(CFrame.new(-r.site.out*13.2*ease(r.stroke))*r.stages.STAGE2.home)
 r.stages.STAGE3.m:PivotTo(cf*r.stages.STAGE3.home)
 r.stages.PUSHER.m:PivotTo(cf*r.stages.PUSHER.home)
 r.emitter:PivotTo(cf*r.emitterHome) -- rigid approved GLB, never stretched
 if r.site.side then
  local g=ease(r.gate);local a=r.site.side*5.85*g
  r.doors.LEAF_LEFT.m:PivotTo(CFrame.new(0,0,a)*r.doors.LEAF_LEFT.home)
  r.doors.LEAF_RIGHT.m:PivotTo(CFrame.new(0,0,-a)*r.doors.LEAF_RIGHT.home)
 end
end
local operating={STARTUP=true,ONLINE=true,WARNING=true,MELTDOWN=true,
 FREEZEDOWN=true,AFTERMATH=true}
local energy=0;local modeLast=nil;local accumulator=0;local orbitTime=0
RunService.Heartbeat:Connect(function(raw)
 accumulator+=math.clamp(raw,0,.2)
 if accumulator<.08 then return end
 local dt=accumulator;accumulator=0;orbitTime+=dt
 local mode=world:GetAttribute("ReactorMode") or "COLD"
 local source=world:GetAttribute("ReactorMeshSignal")==1
 local readyMask=world:GetAttribute("ReactorEmitterReadyMask") or 0
 local brokenMask=world:GetAttribute("ReactorEmitterBrokenMask") or 0
 local failureAge=world:GetAttribute("ReactorMeltdownAge") or 0
 local heatBoost=world:GetAttribute("ReactorLaserBoost")==true
 local gridDrop=world:GetAttribute("ReactorGridDrop")==true
 if not source then mode="COLD";readyMask=0 end
 local pilot=mode=="STARTUP"
 local owner=world:GetAttribute("ReactorPilotOwner")==true
 local ignition=operating[mode] and not pilot and mode~="AFTERMATH"
 local stage=pilot and
  (world:GetAttribute("ReactorPilotStage") or "PILOT_PENDING") or mode
 if mode~=modeLast then
  modeLast=mode;scene:SetAttribute("MotionStatus",mode)
  print("[MESH] R5=",mode,"; six real heads; relay mask=",readyMask)
 end
 scene:SetAttribute("MeshStartupStage",stage)
 local powered=operating[mode]==true
 -- The new pilot script is the ONLY writer of physical GLB poses in STARTUP.
 -- This controller keeps all inherited optics dark and stores its exact
 -- stroke for a smooth reverse or handoff when gameplay changes mode.
 if pilot then
  for _,group in streams do
   for _,ray in group do ray.Enabled=false end
  end
  for _,fx in {sparks,vapor,ignitionCloud,corona} do
   fx.Enabled=false;fx.Rate=0
  end
  for _,orb in orbits do orb.t.Enabled=false end
  coreLamp.Brightness=0
  energy=math.clamp(world:GetAttribute("ReactorPilotWhiteVolume") or 0,0,1)
  for _,r in rigs do
   r.lamp.Brightness=0
   r.leak.Enabled=false;r.shower.Enabled=false
   if owner then
    r.gate=scene:GetAttribute("ReactorPilotGate_"..r.site.tag) or 0
    r.stroke=scene:GetAttribute("ReactorPilotStroke_"..r.site.tag) or 0
   end
   scene:SetAttribute("LiveGate_"..r.site.tag,r.gate)
   scene:SetAttribute("LiveStroke_"..r.site.tag,r.stroke)
  end
  for _,lamp in worklights do
   lamp.Brightness=.85;lamp.Color=Color3.fromRGB(181,211,243)
  end
  scene:SetAttribute("MotionStatus",owner and
   "CHECKPOINT_01_REAL_SIX_HEADS" or "PILOT_NOT_READY")
  scene:SetAttribute("LiveRelayMask",readyMask)
  scene:SetAttribute("LiveBrokenMask",brokenMask)
  return
 end
 for _,l in worklights do
  l.Brightness=gridDrop and .02 or .82
  l.Color=Color3.fromRGB(194,210,228)
 end
 for _,r in rigs do
  local id=r.site.i
  local ready=bit(readyMask,id)
  local broken=bit(brokenMask,id)
  -- Outside STARTUP the existing controller alone owns the rigs.
  local deploy=powered
  if deploy then
   r.gate=toward(r.gate,1,dt/1.55)
   if r.gate>=.999 then r.stroke=toward(r.stroke,1,dt/4) end
  else
   if r.stroke>0 then r.stroke=toward(r.stroke,0,dt/4) end
   if r.stroke<=.003 then r.gate=toward(r.gate,0,dt/1.55) end
  end
  place(r)
  scene:SetAttribute("LiveGate_"..r.site.tag,r.gate)
  scene:SetAttribute("LiveStroke_"..r.site.tag,r.stroke)
  local atTip=ready and r.stroke>=.99 and not broken
  local visual=atTip and ignition and
   (heatBoost and 1 or .87) or 0
  if mode=="MELTDOWN" then
   visual=visual*(.88+.12*math.sin(orbitTime*4+id))
  end
  r.feedGlow=math.clamp(visual,0,1)
  if broken and not r.failed then
   for index,info in r.bendParts do
    local part=info.part
    local drift=r.site.out*(index%2==0 and .46 or .75)
     +Vector3.new(0,-.13*(index%3),index%2==0 and .14 or -.18)
    part.CFrame=CFrame.new(drift)*part.CFrame
     *CFrame.Angles(0,0,math.rad(index%2==0 and 13 or -16))
    part.Material=Enum.Material.Metal
    part.Color=index%3==0 and Color3.fromRGB(145,55,41)
     or Color3.fromRGB(72,49,48)
   end
   r.failed=true;r.emitter:SetAttribute("GLB_HeadCracked",true)
   r.shower:Emit(82)
  elseif not broken and r.failed then
   for _,info in r.bendParts do
    local part=info.part
    part.CFrame=r.emitter:GetPivot()*info.localPose
    part.Material=info.material;part.Color=info.color
    part.Transparency=info.alpha
   end
   r.failed=false;r.emitter:SetAttribute("GLB_HeadCracked",false)
  end
  if broken then
   r.optic.Material=Enum.Material.Metal
   r.optic.Color=Color3.fromRGB(171,63,48)
   r.lamp.Color=Color3.fromRGB(255,69,39)
   r.lamp.Brightness=mode=="MELTDOWN" and
    (.28+.35*math.abs(math.sin(orbitTime*12+id))) or 0
   r.leak.Enabled=mode=="MELTDOWN" or mode=="AFTERMATH"
   r.leak.Rate=17+id*2
   r.shower.Enabled=mode=="MELTDOWN";r.shower.Rate=22+id*2
  else
   r.failed=false
   r.optic.Material=visual>.10 and Enum.Material.Neon
    or Enum.Material.SmoothPlastic
   r.optic.Color=visual>.10 and Color3.fromRGB(132,209,255)
    or Color3.fromRGB(12,76,127)
   r.lamp.Color=Color3.fromRGB(198,234,255)
   r.lamp.Range=8
   r.lamp.Brightness=visual*0.28
   -- Preserve approved metal/nozzle surfaces; let WINDOW__cyan_core glow with live plasma energy when active!
   for _,item in r.detailParts do
    if item.name=="WINDOW__cyan_core" and visual>.10 then
     item.p.Material=Enum.Material.Neon
    else
     item.p.Material=item.material
     item.p.Color=item.color
    end
    item.p.Transparency=item.alpha
   end
   r.leak.Enabled=false;r.shower.Enabled=false
  end
  -- 2D Beam ribbons remain permanently disabled; real 3D coaxial EditableMesh
  -- conduits on the client own all 6 nozzle-to-core energy feeds!
  local pair=streams[id]
  pair[1].Enabled=false
  pair[2].Enabled=false
 end
 local readyForFusion=ignition and powered
 energy=toward(energy,readyForFusion and 1 or 0,dt/2.15)
 local e=ease(energy)
 scene:SetAttribute("LiveCoreEnergy",e)
 for _,info in coreParts do
  local p=info.p
  -- Keep static GLB ray cones, static center spheres, and static un-rotated orbit shells hidden
  -- so ONLY the living 60 FPS 3-axis-rotating & boiling 3D EditableMesh star + coaxial lasers render!
  p.Transparency=1
 end
 local k=(mode=="MELTDOWN" and math.clamp(failureAge/435,0,1) or 0)
 coreLamp.Range=mode=="MELTDOWN" and 46 or 20
 coreLamp.Brightness=e*(0.16+1.95*k)
 coreLamp.Color=mode=="MELTDOWN" and failureAge>230
   and Color3.fromRGB(240,105,172)
  or Color3.fromRGB(220,235,252)
 -- Keep stock 2D center ParticleEmitters & Trails disabled (zero 2D core VFX!).
 sparks.Enabled=false;sparks.Rate=0
 vapor.Enabled=false;vapor.Rate=0
 ignitionCloud.Enabled=false;ignitionCloud.Rate=0
 corona.Enabled=false;corona.Rate=0
 for _,orb in orbits do orb.t.Enabled=false end
 if mode=="COLD" then
  coreLamp.Brightness=0
 end
 -- Lightweight observability for click-free Studio QA; 6 separate feeds.
 scene:SetAttribute("LiveRelayMask",readyMask)
 scene:SetAttribute("LiveBrokenMask",brokenMask)
end)
print("[MESH] Six approved GLBs; real 3D handoff active; 2D core beams/particles disabled.")
