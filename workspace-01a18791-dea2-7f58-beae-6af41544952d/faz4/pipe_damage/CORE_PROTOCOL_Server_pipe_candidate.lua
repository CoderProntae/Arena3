--[[
 Gameplay server: real operator controls, coolant, failure and meltdown.
 CHECKPOINT 01 deletes the former boot score and all startup render logic.
 Only the accepted physical button may enter STARTUP. At this visual gate
 the six approved GLBs move; NO ignition, audio, screen lens or ONLINE yet.
 The user's approval is required before subsequent startup stages exist.
]]

local Players=game:GetService("Players")
local Workspace=game:GetService("Workspace")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local Lighting=game:GetService("Lighting")
local TweenService=game:GetService("TweenService")
local RunService=game:GetService("RunService")
local Debris=game:GetService("Debris")

local CFG={
	STUDIO_AUTO_STARTUP=false, -- Studio ONLY: autonomous visual preview. No clicks.
	STUDIO_AUTO_MELTDOWN=false, -- Studio ONLY: start a test 12 seconds after Play.
	STUDIO_PREVIEW_SECOND=0, -- Optional: 244 resembles user's 15:53 screenshot.
	SILENT_PROTOTYPE=true, -- Visual only: unverified catalog audio remains muted.
	-- Accepted physical START input is the one authoritative age zero.
	-- The old video timestamp does not control gameplay.
	MELTDOWN_SECONDS=435,       -- Reference's first chapter: 11:49 to 19:04.
	RESET_DELAY=57,
	SHUTDOWN_RESCUE_UNTIL=270,
	MAX_DEBRIS=245,
	INTERACTION_DISTANCE=11, -- avatar-sized room; server validates EVERY click.
	-- Exposure is an ART DIRECTION constraint, not a performance switch.
	-- V1's whiteout came from 30-brightness core lights with 120-stud
	-- reach, 0.9-1.55 bloom and an overlarge glowing control console.
	VISUAL={
		ROOM_EXPOSURE=-0.24,
		BLOOM_THRESHOLD=1.88,
		BLOOM_IDLE=0.20,
		BLOOM_MELTDOWN=0.35,
		CORE_LIGHT_RANGE=59, -- Star at z=26; glass z=93: >67 away.
		CORE_LIGHT_IDLE=2.25,
		CORE_LIGHT_MAX=5.4,
		PHYSICAL_BUTTON_NEON_ALPHA=0.52,
	},
	AUDIO={
		opening="rbxassetid://1843973421", -- Roblox Creator Store score
		escalation="rbxassetid://9040229071",
		finale="rbxassetid://9042675817",
		idle="rbxassetid://9112775175",
		turbine="rbxassetid://9118747525",
		siren="rbxassetid://9113073742",
		siren2="rbxassetid://9113073796",
		panel="rbxassetid://9120099286",
		switch="rbxassetid://9120099286",
		laser="rbxassetid://9116231442",
		pressure="rbxassetid://9117895914",
		coolant="rbxassetid://9120562287",
		plasma="rbxassetid://9125742111",
		hiss="rbxassetid://9117665655",
		electricity="rbxassetid://9114247505",
		steel="rbxassetid://9116554136",
		rupture="rbxassetid://9116546593",
		glass="rbxassetid://7140153519",
		quake="rbxassetid://9114224217",
		impact="rbxassetid://9120705982",
		explosion="rbxassetid://9114363548",
		gate="rbxassetid://9114307430",
		rain="rbxassetid://9112854440",
	},
}
local C={
	white=Color3.fromRGB(252,252,255),
	porcelain=Color3.fromRGB(233,228,228),
	silver=Color3.fromRGB(151,168,183),
	trim=Color3.fromRGB(92,105,117),
	slate=Color3.fromRGB(42,51,66),
	charcoal=Color3.fromRGB(23,30,43),
	black=Color3.fromRGB(9,14,25),
	cobalt=Color3.fromRGB(26,77,203),
	azure=Color3.fromRGB(38,168,253),
	cyan=Color3.fromRGB(97,244,251),
	violet=Color3.fromRGB(137,65,255),
	magenta=Color3.fromRGB(251,72,246),
	mint=Color3.fromRGB(98,245,161),
	amber=Color3.fromRGB(252,185,51),
	orange=Color3.fromRGB(252,98,36),
	red=Color3.fromRGB(251,43,53),
	burgundy=Color3.fromRGB(96,20,28),
	chamber=Color3.fromRGB(143,72,49),
	floor=Color3.fromRGB(222,218,223),
	floorInset=Color3.fromRGB(207,207,214),
	wall=Color3.fromRGB(196,191,193),
	ivory=Color3.fromRGB(247,240,233),
	warm=Color3.fromRGB(255,197,170),
	frame=Color3.fromRGB(80,75,79),
	midnight=Color3.fromRGB(5,12,32),
	navy=Color3.fromRGB(21,54,123),
	nebula=Color3.fromRGB(39,110,208),
	ruby=Color3.fromRGB(141,24,37),
}
-- All original authored coordinates are expressed in design units.
-- Human scale, NOT a giant doll: building, machines and controls together
-- are half-size. The unmodified 5-6-stud Roblox character can now reach
-- a chest-height lever; the control-room ceiling is ~29, not ~58 studs.
local WORLD_SCALE=0.50
local UNITS=Vector3
local FRAME=CFrame
local Vector3={
	new=function(x,y,z)
		return UNITS.new((x or 0)*WORLD_SCALE,
			(y or 0)*WORLD_SCALE,(z or 0)*WORLD_SCALE)
	end,
	zero=UNITS.zero,
}
local CFrame={
	new=function(x,y,z)
		if type(x)=="number" or x==nil then
			return FRAME.new((x or 0)*WORLD_SCALE,
				(y or 0)*WORLD_SCALE,(z or 0)*WORLD_SCALE)
		end
		-- A Vector3 passed here ALREADY represents world-space studs.
		return FRAME.new(x)
	end,
	lookAt=FRAME.lookAt,
	Angles=FRAME.Angles,
}
local TAU=2*math.pi
local CORE=Vector3.new(0,53,0)
local rng=Random.new(52570)
local now=time
local SPARK="rbxasset://textures/particles/sparkles_main.dds"
local SMOKE="rbxasset://textures/particles/smoke_main.dds"

do
	local previous=Workspace:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
	if previous then previous:Destroy() end
	local priorRemote=ReplicatedStorage:FindFirstChild("CORE_PROTOCOL_V2_CUES")
	if priorRemote then priorRemote:Destroy() end
end
for _,id in ipairs({"CORE_PROTOCOL_BLOOM","CORE_PROTOCOL_GRADE",
	"CORE_PROTOCOL_ATMOS","CORE_PROTOCOL_RAYS",
	"CORE_PROTOCOL_V2_BLOOM","CORE_PROTOCOL_V2_GRADE",
	"CORE_PROTOCOL_V2_ATMOS","CORE_PROTOCOL_V2_RAYS"}) do
	local e=Lighting:FindFirstChild(id)
	if e then e:Destroy() end
end
local remote=Instance.new("RemoteEvent")
remote.Name="CORE_PROTOCOL_V2_CUES"
remote.Parent=ReplicatedStorage
local world=Instance.new("Model")
world.Name="CORE_PROTOCOL_V2_WORLD"
world.Parent=Workspace
world:SetAttribute("SilentPrototype",CFG.SILENT_PROTOTYPE)
pcall(function() world.ModelStreamingMode=Enum.ModelStreamingMode.Persistent end)
local function folder(parent,name)
	local f=Instance.new("Folder")
	f.Name=name;f.Parent=parent
	return f
end
local chamber=folder(world,"01_CONTAINMENT")
local gallery=folder(world,"02_PANORAMIC_CONTROL_ROOM")
local machine=folder(world,"03_STAR_REACTOR")
local service=folder(world,"04_REACTOR_SERVICE_CORRIDORS")
local interfaces=folder(world,"05_WORKING_MACHINERY")
local damage=folder(world,"06_DAMAGE_THAT_STAYS")
local transient=folder(damage,"MOMENTARY_SHARDS")
local fractures=folder(damage,"PERMANENT_SCARS")
local soundAnchors=folder(world,"07_SPATIAL_SOUNDS")

local bloom=Instance.new("BloomEffect")
bloom.Name="CORE_PROTOCOL_V2_BLOOM"
bloom.Intensity=CFG.VISUAL.BLOOM_IDLE
bloom.Size=22;bloom.Threshold=CFG.VISUAL.BLOOM_THRESHOLD
bloom.Parent=Lighting
local grade=Instance.new("ColorCorrectionEffect")
grade.Name="CORE_PROTOCOL_V2_GRADE";grade.Contrast=0.045;grade.Brightness=0.055
grade.Saturation=0.015;grade.TintColor=Color3.fromRGB(252,249,246)
grade.Parent=Lighting
local atmosphere=Instance.new("Atmosphere")
atmosphere.Name="CORE_PROTOCOL_V2_ATMOS";atmosphere.Density=0.012
atmosphere.Haze=0.018;atmosphere.Color=Color3.fromRGB(120,145,191)
atmosphere.Decay=Color3.fromRGB(9,17,37)
atmosphere.Parent=Lighting
do
	local sunrays=Instance.new("SunRaysEffect")
	sunrays.Name="CORE_PROTOCOL_V2_RAYS";sunrays.Intensity=0.0
	sunrays.Spread=0.5;sunrays.Parent=Lighting
end
Lighting.ClockTime=0
Lighting.Brightness=2.05
Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE
Lighting.Ambient=Color3.fromRGB(138,137,142)
Lighting.OutdoorAmbient=Color3.fromRGB(59,58,70)
Lighting.FogColor=Color3.fromRGB(9,17,37)
Lighting.FogStart=225;Lighting.FogEnd=530

local function part(parent,name,cf,size,color,material,alpha,collide,shape)
	local p=Instance.new("Part")
	p.Name=name;p.CFrame=cf;p.Size=size
	p.Color=color or C.silver;p.Material=material or Enum.Material.Metal
	p.Transparency=alpha or 0;p.Anchored=true
	p.CanCollide=collide==true;p.CanTouch=collide==true
	p.CastShadow=(p.Material~=Enum.Material.Neon)
	p.TopSurface=Enum.SurfaceType.Smooth
	p.BottomSurface=Enum.SurfaceType.Smooth
	if shape then p.Shape=shape end
	p.Parent=parent
	return p
end
local function box(parent,name,pos,size,color,mat,alpha,collide)
	return part(parent,name,CFrame.new(pos),size,color,mat,alpha,collide)
end
local function ball(parent,name,pos,r,color,mat,alpha,collide)
	return part(parent,name,CFrame.new(pos),Vector3.new(2*r,2*r,2*r),
		color,mat,alpha,collide,Enum.PartType.Ball)
end
local function beam(parent,name,a,b,width,color,mat,alpha,collide)
	local length=(b-a).Magnitude
	if length<0.01 then return nil end
	return part(parent,name,CFrame.lookAt((a+b)/2,b),
		UNITS.new(width*WORLD_SCALE,width*WORLD_SCALE,length),
		color,mat,alpha,collide)
end
local function tube(parent,name,a,b,r,color,mat,alpha,collide)
	local length=(b-a).Magnitude
	if length<0.01 then return nil end
	return part(parent,name,CFrame.lookAt((a+b)/2,b)*
		CFrame.Angles(0,math.pi/2,0),
		UNITS.new(length,2*r*WORLD_SCALE,2*r*WORLD_SCALE),
		color,mat,alpha,collide,Enum.PartType.Cylinder)
end
local function cylY(parent,name,center,r,height,color,mat,alpha,collide)
	return part(parent,name,CFrame.new(center)*CFrame.Angles(0,0,math.pi/2),
		Vector3.new(height,2*r,2*r),color,mat,alpha,collide,
		Enum.PartType.Cylinder)
end
local function circleXY(parent,name,center,r,n,width,color,mat,alpha)
	local pieces={}
	for i=0,n-1 do
		local a=i*TAU/n;local b=(i+1)*TAU/n
		local p=center+Vector3.new(math.cos(a)*r,math.sin(a)*r,0)
		local q=center+Vector3.new(math.cos(b)*r,math.sin(b)*r,0)
		pieces[#pieces+1]=beam(parent,name.."_"..i,p,q,width,color,mat,alpha)
	end
	return pieces
end
local function circleXZ(parent,name,center,r,n,width,color,mat,alpha)
	local pieces={}
	for i=0,n-1 do
		local a=i*TAU/n;local b=(i+1)*TAU/n
		local p=center+Vector3.new(math.cos(a)*r,0,math.sin(a)*r)
		local q=center+Vector3.new(math.cos(b)*r,0,math.sin(b)*r)
		pieces[#pieces+1]=beam(parent,name.."_"..i,p,q,width,color,mat,alpha)
	end
	return pieces
end
local function lamp(parent,color,power,range)
	local l=Instance.new("PointLight")
	l.Color=color;l.Brightness=power
	l.Range=math.min(range*WORLD_SCALE,120)
	l.Shadows=false;l.Parent=parent
	return l
end
local function particles(parent,name,texture,rate,color,initial,final,speed)
	local e=Instance.new("ParticleEmitter")
	e.Name=name;e.Texture=texture;e.Enabled=false;e.Rate=rate
	e.Speed=NumberRange.new(speed*0.5,speed)
	e.Lifetime=NumberRange.new(0.7,1.9)
	e.SpreadAngle=Vector2.new(65,65)
	e.Color=ColorSequence.new(color,color)
	e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,initial*WORLD_SCALE),
		NumberSequenceKeypoint.new(1,final*WORLD_SCALE)})
	e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,0.13),
		NumberSequenceKeypoint.new(1,1)})
	e.LightEmission=0.8;e.Parent=parent
	return e
end
local function soundtrack(id,parent,name,volume,looped,range)
	if CFG.SILENT_PROTOTYPE or not id or id=="" then return nil end
	local a=Instance.new("Sound")
	a.Name=name;a.SoundId=id;a.Volume=volume or 0.5
	a.Looped=looped==true
	a.RollOffMaxDistance=(range or 260)*WORLD_SCALE
	a.Parent=parent
	return a
end
local function sfx(key,parent,volume,pitch,seconds)
	if CFG.SILENT_PROTOTYPE then return end
	local id=CFG.AUDIO[key]
	if not id then return end
	local a=soundtrack(id,parent,"SFX_"..key,volume or 0.6,false,280)
	a.PlaybackSpeed=pitch or 1;a:Play()
	Debris:AddItem(a,seconds or 17)
end
local function tween(object,seconds,properties,style)
	local t=TweenService:Create(object,TweenInfo.new(seconds,
		style or Enum.EasingStyle.Quad,Enum.EasingDirection.Out),properties)
	t:Play();return t
end
local function caption(parent,face,text,textSize,fg,canvas)
	-- In-world SurfaceGui on a real piece of equipment, NOT screen HUD.
	local gui=Instance.new("SurfaceGui")
	gui.Name="ENGRAVED_VIEW";gui.Face=face
	local pixels=canvas or Vector2.new(880,300)
	gui.CanvasSize=Vector2.new(math.max(100,math.floor(pixels.X*WORLD_SCALE)),
		math.max(64,math.floor(pixels.Y*WORLD_SCALE)))
	gui.LightInfluence=0;gui.AlwaysOnTop=false;gui.Parent=parent
	local label=Instance.new("TextLabel")
	label.Name="INSCRIPTION"
	label.BackgroundTransparency=1
	label.Size=UDim2.fromScale(1,1)
	label.Text=text or ""
	label.TextWrapped=true
	label.TextColor3=fg or C.white
	label.TextStrokeTransparency=0.13
	label.TextSize=math.max(13,math.floor((textSize or 48)*WORLD_SCALE))
	label.Font=Enum.Font.Code
	label.Parent=gui
	return label
end
local function ePanel(parent,name,pos,size,text,tint,face,textSize)
	local b=box(parent,name,pos,size,C.charcoal,Enum.Material.Metal)
	local display=box(parent,name.."_LIT_SCREEN",
		pos+Vector3.new(0,0,(face==Enum.NormalId.Back and 1 or -1)
			*(size.Z/WORLD_SCALE/2+0.15)),
		Vector3.new(size.X/WORLD_SCALE-0.6,
			size.Y/WORLD_SCALE-0.55,0.18),
		tint or C.black,Enum.Material.SmoothPlastic,0.04)
	local gui=caption(display,face or Enum.NormalId.Back,text,
		textSize or 75,C.white,
		Vector2.new(math.floor((size.X/WORLD_SCALE-0.6)*44),
			math.floor((size.Y/WORLD_SCALE-0.55)*44)))
	gui.TextScaled=false;gui.TextWrapped=false
	gui.Font=Enum.Font.GothamBold
	gui.TextStrokeTransparency=0.76
	gui.TextXAlignment=Enum.TextXAlignment.Center
	gui.TextYAlignment=Enum.TextYAlignment.Center
	gui.Size=UDim2.fromScale(0.96,0.88)
	gui.Position=UDim2.fromScale(0.02,0.06)
	return {outer=b,screen=display,label=gui}
end
local function fracture(from,to,n,tint,parent)
	local last=from
	for i=1,n do
		local p=from:Lerp(to,i/n)
		if i<n then p=p+Vector3.new(rng:NextNumber(-2.6,2.6),
			rng:NextNumber(-2.6,2.6),rng:NextNumber(-2.6,2.6)) end
		local seg=beam(parent or transient,"ERRATIC_DISCHARGE",last,p,
			rng:NextNumber(0.16,0.48),tint or C.cyan,
			Enum.Material.Neon,0.04)
		if parent==nil and seg then Debris:AddItem(seg,0.32) end
		last=p
	end
end
local function throwShard(ref,color,scale,velocity,life)
	if #transient:GetChildren()>=CFG.MAX_DEBRIS then return end
	local wasNeon=ref.Material==Enum.Material.Neon
	local shard=part(transient,"REAL_FALLING_SHRAPNEL",ref.CFrame,
		ref.Size*math.min(scale or 0.6,0.76),
		wasNeon and C.trim or color or ref.Color,
		wasNeon and Enum.Material.Metal or ref.Material,
		0.03,true,ref.Shape)
	shard.Anchored=false
	shard.AssemblyLinearVelocity=velocity or Vector3.new(0,18,18)
	shard.AssemblyAngularVelocity=Vector3.new(rng:NextNumber(-8,8),
		rng:NextNumber(-8,8),rng:NextNumber(-8,8))
	Debris:AddItem(shard,life or 13)
end
local state -- declared before shake so auxiliary controls cannot shake STARTUP
local function shake(power,duration)
	if state and state.mode=="STARTUP" then return end
	remote:FireAllClients("SHAKE",power,duration)
end
local function flash(power,hue)
	remote:FireAllClients("FLASH",power,hue)
end
local function centerPulse(radius,duration,color)
	-- The V1 pulse grew to a 187-STUD white sphere; it physically crossed
	-- the 93-stud observation plane and overexposed the entire control room.
	-- The cinematic belongs BEHIND the glass. World-space diameter <= 52.
	local safeDiameter=math.min(52,math.max(8,radius*4.6))
	local spark=ball(transient,"CHAMBER_ONLY_PLASMA_SURGE",
		CORE+Vector3.new(0,0,23),
		math.min(1.7,radius*0.35),color or C.magenta,
		Enum.Material.Neon,0.66)
	spark.CastShadow=false
	local shower=particles(spark,"RADIAL_WHITE_HOT_DISCHARGE",
		SPARK,0,color or C.ivory,0.62,0.045,32)
	shower.SpreadAngle=Vector2.new(180,180)
	shower.Lifetime=NumberRange.new(0.32,0.78)
	shower:Emit(math.floor(16+radius*4))
	tween(spark,duration,{Size=Vector3.new(safeDiameter,safeDiameter,
		safeDiameter),Transparency=1},Enum.EasingStyle.Quart)
	Debris:AddItem(spark,duration+0.25)
end
local function outwardFrontWave(first,last,seconds,color)
	local wave={}
	for i=0,35 do
		local a=i*TAU/36;local b=(i+1)*TAU/36
		wave[#wave+1]=beam(transient,"WINDOW_FACING_SHOCK_RING",
			CORE+Vector3.new(math.cos(a)*first,math.sin(a)*first,29),
			CORE+Vector3.new(math.cos(b)*first,math.sin(b)*first,29),
			1.05,color or C.violet,Enum.Material.Neon,0.48)
	end
	task.spawn(function()
		local started=now()
		while now()-started<seconds do
			local u=math.clamp((now()-started)/seconds,0,1)
			local r=first+(last-first)*u
			for i,p in ipairs(wave) do
				local a=(i-1)*TAU/36;local b=i*TAU/36
				local x=CORE+Vector3.new(math.cos(a)*r,math.sin(a)*r,29)
				local y=CORE+Vector3.new(math.cos(b)*r,math.sin(b)*r,29)
				p.CFrame=CFrame.lookAt((x+y)/2,y)
				p.Size=UNITS.new(1.05*WORLD_SCALE,1.05*WORLD_SCALE,
					(y-x).Magnitude)
				p.Transparency=0.48+0.51*u
			end
			task.wait(0.085)
		end
		for _,p in ipairs(wave) do p:Destroy() end
	end)
end

-- ================================================================
-- 1. RECTANGULAR CONTAINMENT: red/orange hazard bay, blue plasma backdrop.
-- ================================================================
-- R5's large OLD, non-approved outer chamber base showed as red slabs and
-- a black/orange-striped floor around the seven approved GLBs. Retint only
-- those procedural BACKGROUND Parts to the blue-grey 360p facility palette.
-- Their replacements as original GLBs remain a separate review task.
box(chamber,"INDUSTRIAL_FLOOR",Vector3.new(0,-2,-4),
	Vector3.new(192,4,188),Color3.fromRGB(34,48,73),
	Enum.Material.DiamondPlate,0,true)
box(chamber,"DARK_CORE_STAGE",Vector3.new(0,0.12,0),
	Vector3.new(132,0.22,119),Color3.fromRGB(50,64,91),
	Enum.Material.Metal,0,true)
box(chamber,"BACK_CONTAINMENT_WALL",Vector3.new(0,56,-92),
	Vector3.new(194,112,3.3),Color3.fromRGB(55,73,103),
	Enum.Material.Metal,0,true)
box(chamber,"LEFT_CONTAINMENT_WALL",Vector3.new(-96,55,-2),
	Vector3.new(3.4,110,183),Color3.fromRGB(55,73,103),
	Enum.Material.Metal,0,true)
box(chamber,"RIGHT_CONTAINMENT_WALL",Vector3.new(96,55,-2),
	Vector3.new(3.4,110,183),Color3.fromRGB(55,73,103),
	Enum.Material.Metal,0,true)
box(chamber,"RIBBED_CEILING",Vector3.new(0,110,-3),
	Vector3.new(192,3,188),C.slate,Enum.Material.Metal,0,true)
for _,wallX in ipairs({-65,65}) do
	box(chamber,"GIANT_REAR_SAFETY_PANEL",Vector3.new(wallX,57,-88.9),
		Vector3.new(43,61,0.5),C.charcoal,Enum.Material.Metal)
	box(chamber,"RECESS_ORANGE_ARMOR",Vector3.new(wallX,54,-88.5),
		Vector3.new(36,47,0.4),C.chamber,Enum.Material.Metal)
	box(chamber,"HAZARD_HATCH",Vector3.new(wallX,55,-88.1),
		Vector3.new(26,29,0.3),C.black,Enum.Material.Metal)
	for row=1,6 do
		local y=33+(row-1)*8.4
		beam(chamber,"BACK_PANEL_HAZARD_SHEVRON",
			Vector3.new(wallX-17,y,-87.65),
			Vector3.new(wallX+17,y,-87.65),
			0.42,row%2==0 and C.orange or C.amber,
			Enum.Material.Neon,0.13)
		for col=1,4 do
			box(chamber,"HATCH_VENT_BLADE",
				Vector3.new(wallX-12+col*4.8,y+2.5,-87.6),
				Vector3.new(3.6,1.16,0.28),C.slate,Enum.Material.Metal)
		end
	end
	for _,x in ipairs({wallX-21,wallX+21}) do
		beam(chamber,"REAR_INNER_LUMINESCENT_TRIM",
			Vector3.new(x,17,-88),Vector3.new(x,97,-88),
			0.64,C.orange,Enum.Material.Neon,0.19)
	end
end
box(chamber,"MIDNIGHT_BACK_CORE_RECESS",Vector3.new(0,57,-90.3),
	Vector3.new(57,87,0.5),C.black,Enum.Material.Metal)
for side=-1,1,2 do
	local x=side*85
	for row=0,12 do
		local y=12+row*7.4
		local plate=box(chamber,"CONTAINMENT_PANEL_SEAM",
			Vector3.new(x,y,-44),Vector3.new(0.12,0.26,84),
			row%3==0 and C.orange or C.trim,
			row%3==0 and Enum.Material.Neon or Enum.Material.Metal,
			row%3==0 and 0.23 or 0)
		plate.CastShadow=false
	end
end
for i=0,19 do
	local x=-91+i*9.6
	beam(chamber,"CHAMBER_CEILING_SERVICE_RAIL",
		Vector3.new(x,107,-89),Vector3.new(x,107,82),
		i%4==0 and 0.68 or 0.19,
		i%4==0 and C.trim or C.slate,Enum.Material.Metal)
end
local chamberServiceLights={}
for i=0,23 do
	local x=-84+(i%12)*15.2
	local z=-69+math.floor(i/12)*111
	local lightPart=ball(chamber,"CAMBER_BEAM_LAMP",
		Vector3.new(x,102,z),0.62,
		i%3==0 and C.violet or C.azure,Enum.Material.Neon)
	if i%4==0 then
		chamberServiceLights[#chamberServiceLights+1]=
			lamp(lightPart,C.violet,0.68,35)
	end
end
for x=-84,84,12 do
	beam(chamber,"COLD_BLUE_FLOOR_SERVICE_HAIRLINE",
		Vector3.new(x,0.29,-74),Vector3.new(x,0.29,79),
		0.11,Color3.fromRGB(137,177,227),Enum.Material.Neon,0.68)
end
for _,z in ipairs({-72,77}) do
	for i=0,18 do
		box(chamber,"BOUNDARY_HAZARD_BAND",
			Vector3.new(-87+i*9.6,0.41,z),Vector3.new(4,0.12,0.92),
			i%2==0 and C.amber or C.black,
			i%2==0 and Enum.Material.Neon or Enum.Material.Metal,
			i%2==0 and 0.21 or 0)
	end
end

-- ================================================================
-- 2. CONTROL LAB: MUTED WARM TILE, BLACK LIFT, DARK-FRAMED GLASS.
-- ================================================================
local floor=box(gallery,"LOW_SHEEN_WARM_LAB_FLOOR",Vector3.new(0,22.3,127),
	Vector3.new(126,3.4,72),C.floor,
	Enum.Material.SmoothPlastic,0,true)
floor.Reflectance=0.025
for ix=-5,5 do
	for iz=0,6 do
		local tile=box(gallery,"SETBACK_GREY_CERAMIC_TILE",
			Vector3.new(ix*10.6,24.06,98+iz*9.4),
			Vector3.new(10.35,0.075,9.16),
			(ix+iz)%4==0 and C.floor or C.floorInset,
			Enum.Material.SmoothPlastic,0.03)
		tile.Reflectance=0.015
	end
end
-- Recessed black square in the reference becomes a functional lift bay (stepped +0.065 above ceramic tiles -> %0 Z-fight!)
box(gallery,"FLOOR_LIFT_DARK_RECESS",Vector3.new(0,24.215,128),
	Vector3.new(40,0.10,29),C.black,
	Enum.Material.SmoothPlastic,0.03)
local pitTrim={}
for _,line in ipairs({
	{Vector3.new(-20,24.28,113.4),Vector3.new(20,24.28,113.4)},
	{Vector3.new(-20,24.28,142.6),Vector3.new(20,24.28,142.6)},
	{Vector3.new(-20,24.28,113.4),Vector3.new(-20,24.28,142.6)},
	{Vector3.new(20,24.28,113.4),Vector3.new(20,24.28,142.6)},
	}) do
	pitTrim[#pitTrim+1]=beam(gallery,"RECESSED_LIFT_EDGE_HAIRLINE",
		line[1],line[2],0.18,C.ivory,Enum.Material.Neon,0.58)
end
box(gallery,"RECESSED_METAL_GRILLE_CEILING",
	Vector3.new(0,81.8,127.2),
	Vector3.new(130,3.5,73),C.frame,Enum.Material.Metal,0,true)
-- Screwed-in ceramic ceiling cassettes, exposed dark service rails and
-- black vents replace the bare flat V3 slab. All strips remain behind lamps.
for ix=-2,2 do
	for iz=0,5 do
		local x=ix*24
		local z=99+iz*11.5
		box(gallery,"PATINATED_RECESSED_CEILING_CASSETTE",
				Vector3.new(x,79.82,z),Vector3.new(22.5,0.22,10.2),
				(ix+iz)%4==0 and Color3.fromRGB(175,173,177)
					or Color3.fromRGB(119,125,137),
				Enum.Material.Metal,0.025)
		box(gallery,"BLACK_AIRFLOW_VENT_GRILLE",
			Vector3.new(x,79.63,z+2.9),
			Vector3.new(16.2,0.11,3.3),C.charcoal,
				Enum.Material.Metal)
		for slit=-4,4 do
			beam(gallery,"VENT_HAIRLINE",
				Vector3.new(x+slit*1.45,79.55,z+2.0),
				Vector3.new(x+slit*1.45,79.55,z+3.9),
				0.06,C.trim,Enum.Material.Metal)
		end
	end
end
box(gallery,"LAB_REAR_WALL_LEFT",Vector3.new(-37,52,163),
	Vector3.new(53,57,2.1),C.wall,Enum.Material.Metal,0,true)
box(gallery,"LAB_REAR_WALL_RIGHT",Vector3.new(37,52,163),
	Vector3.new(53,57,2.1),C.wall,Enum.Material.Metal,0,true)
box(gallery,"REAR_DOOR_HEADER",Vector3.new(0,68,163),
	Vector3.new(20.92,22,1.94),C.trim,Enum.Material.Metal,0,true)
for _,side in ipairs({-1,1}) do
	for _,data in ipairs({{108,34},{152,22}}) do
		box(gallery,"CONTROL_ROOM_SIDE_WALL_SEGMENT",
			Vector3.new(side*62,52,data[1]),
			Vector3.new(2.3,57,data[2]),C.wall,
			Enum.Material.Metal,0,true)
	end
	box(gallery,"SIDE_DOOR_OVERHEAD_LINTEL",
		Vector3.new(side*62,62,133.0),
		Vector3.new(2.12,38,15.92),C.silver,Enum.Material.Metal,0,true)
	beam(gallery,"SIDE_EXIT_DIM_STATUS_CABLE",
		Vector3.new(side*60.75,42,124),
		Vector3.new(side*60.75,42,140),0.16,C.mint,
		Enum.Material.Neon,0.66)
end
-- White inset perimeter panels, cable runners and visible fasteners.
for _,side in ipairs({-1,1}) do
	for n=0,4 do
		local z=101+n*12.9
		beam(gallery,"CONTROL_LAB_PANEL_VERTICAL_JOINT",
			Vector3.new(side*60.35,29,z),
			Vector3.new(side*60.35,75,z),
			0.12,C.trim,Enum.Material.Metal)
		for _,y in ipairs({32,68}) do
			ball(gallery,"SIDE_WALL_COUNTERSUNK_BOLT",
				Vector3.new(side*60.25,y,z+1.0),0.17,
				C.silver,Enum.Material.Metal)
		end
	end
end
-- Laminated VISUAL pane: Glass material erases translucent Neon and
-- particles behind it in Roblox's renderer, even at 98% transparency.
-- Thin SmoothPlastic preserves the glass boundary AND the whole reactor.
box(gallery,"FRONT_WINDOW_LOW_DARK_SILL",
	Vector3.new(0,25.15,93.3),
	Vector3.new(126,2.6,2.5),C.frame,Enum.Material.Metal,0,true)
box(gallery,"FRONT_WINDOW_UPPER_BURGUNDY_ARCH",
	Vector3.new(0,77.0,93.3),
	Vector3.new(126,11,2.5),C.frame,Enum.Material.Metal,0,true)
for _,side in ipairs({-1,1}) do
	box(gallery,"WINDOW_HEAVY_SIDE_COLUMN",
		Vector3.new(side*57.3,50.8,93.4),
		Vector3.new(9.6,49.2,3.6),C.frame,
		Enum.Material.Metal,0,true)
end
local glassPanes={}
-- Two laminated panels meet at x=43. This leaves both emitters and
-- the star visible from the centered camera and the default spawn.
for i,spec in ipairs({{-5.5,97.0},{48.5,11.0}}) do
	local pane=box(gallery,"PANORAMIC_LAMINATED_GLASS_"..i,
		Vector3.new(spec[1],49.25,93.25),
		Vector3.new(spec[2],45.0,0.4),
		C.ivory,Enum.Material.SmoothPlastic,0.985,true)
	pane.Reflectance=0.045
	glassPanes[#glassPanes+1]=pane
end
box(gallery,"SLIM_OFFSET_GLASS_MULLION",
	Vector3.new(43,49.25,93.5),
	Vector3.new(0.72,45.0,1.2),
	C.frame,Enum.Material.Metal)
for _,y in ipairs({26.68,71.95}) do
	beam(gallery,"VIEWING_WINDOW_DARK_EDGE",
		Vector3.new(-54,y,94),Vector3.new(54,y,94),
		0.16,C.ruby,Enum.Material.Neon,0.71)
end
for _,side in ipairs({-1,1}) do
	beam(gallery,"GLASS_PERIMETER_DARK_TRIM",
		Vector3.new(side*54,26.7,94),
		Vector3.new(side*54,71.9,94),0.24,C.frame,
		Enum.Material.Metal,0)
end
-- Permanent instrument-wall occupancy on the LEFT of the glass, as in
-- the reference frame. It does NOT move or ever cover the core at x~=0.
-- Main sightline crosses at x≈-18; LEFT projector head at x≈-31.
-- Rack's right edge is x=-36: none of the SIX emitter heads is hidden.
box(gallery,"PERMANENT_LEFT_INSTRUMENT_BACKPLATE",
	Vector3.new(-45,50.4,95.22),Vector3.new(18,40.4,1.0),
	C.frame,Enum.Material.Metal,0,true)
local frontStatusLamps={}
for group=0,1 do
	local sx=-50.1+group*9.15
	box(gallery,"INDICATOR_BANK_BAKELITE_RECESS",
		Vector3.new(sx,65.5,95.96),Vector3.new(7.2,3.0,0.22),
		C.black,Enum.Material.Metal)
	for index=0,7 do
		local light=box(gallery,"SMALL_RED_STATUS_LED_NOT_BUTTON",
			Vector3.new(sx-2.65+(index%4)*1.75,
				66.15-math.floor(index/4)*1.18,96.15),
			Vector3.new(0.88,0.45,0.12),C.ruby,
			Enum.Material.Neon,0.38)
		frontStatusLamps[#frontStatusLamps+1]={part=light,
			group=group,index=index}
	end
end
local leftFrontTelemetry=ePanel(gallery,
	"VISIBLE_FRONT_WALL_GENERATOR_DIAGNOSTIC",
	Vector3.new(-47.8,53.2,95.88),
	Vector3.new(12.2,10.1,0.38),
	"CORE COLD\nPWR 000%\nTEMP 0026C",
	C.black,Enum.NormalId.Back,83)
local leftFrontCoolant=ePanel(gallery,
	"VISIBLE_FRONT_WALL_COOLANT_DIAGNOSTIC",
	Vector3.new(-47.8,39.0,95.88),
	Vector3.new(12.2,9.7,0.38),
	"FLOW 050%\nE-COOL 100%\nKEYS 0/3",
	C.black,Enum.NormalId.Back,81)
-- A visibly readable left-wall stack, not distant 8-pixel digits.
leftFrontTelemetry.label.TextXAlignment=Enum.TextXAlignment.Left
leftFrontCoolant.label.TextXAlignment=Enum.TextXAlignment.Left
leftFrontTelemetry.label.Position=UDim2.fromScale(0.065,0.06)
leftFrontCoolant.label.Position=UDim2.fromScale(0.065,0.06)
local frontIndicatorCells={}
for row=0,6 do
	for col=0,3 do
		local color=(row+col)%6==0 and C.amber
			or (row*3+col)%7==0 and C.red or C.azure
		local diode=box(gallery,"AMBER_AND_BLUE_STATUS_PIXELS",
			Vector3.new(-40.2+col*1.05,57.5-row*2.29,96.1),
			Vector3.new(0.63,0.83,0.13),color,
			Enum.Material.Neon,0.53)
		frontIndicatorCells[#frontIndicatorCells+1]={part=diode,
			row=row,col=col,normal=color}
	end
end
for _,y in ipairs({30.8,47.6,63.9,69.9}) do
	beam(gallery,"LEFT_INSTRUMENT_EXPOSED_DARK_TRIM",
		Vector3.new(-53.9,y,96.07),
		Vector3.new(-36.1,y,96.07),
		0.13,C.trim,Enum.Material.Metal)
end
-- 360p gallery: thin BLACK status letterbox above the glass, with white
-- terminal type. The previous 5.7-unit glowing WHITE slab obscured the
-- upper physical emitter and washed out half the observation window.
local mainSign=ePanel(gallery,"OVER_WINDOW_EMERGENCY_LETTERBOX",
	Vector3.new(0,77.2,95.05),Vector3.new(48,3.3,0.55),
	"AWAITING STARTUP...",C.black,Enum.NormalId.Back,66)
mainSign.outer.Color=C.frame
mainSign.screen.Color=Color3.fromRGB(11,17,30)
mainSign.screen.Material=Enum.Material.SmoothPlastic
mainSign.screen.Transparency=0
mainSign.label.TextSize=math.floor(75*WORLD_SCALE)
mainSign.label.Font=Enum.Font.Code
mainSign.label.TextColor3=C.ivory
local coreReadout=ePanel(gallery,"CENTER_PHYSICAL_REACTOR_STATUS",
	Vector3.new(0,72.0,95.18),Vector3.new(29,2.4,0.45),
	"CORE 0026C  /  PRESS 018",C.black,
	Enum.NormalId.Back,56)
local leftReadout=ePanel(gallery,"LEFT_COOLANT_STATUS",
	Vector3.new(-39,73.7,95.15),Vector3.new(24,3.7,0.4),
	"COOLANT 050%",C.black,Enum.NormalId.Back,73)
local rightReadout=ePanel(gallery,"RIGHT_SYSTEM_STATUS",
	Vector3.new(39,73.7,95.15),Vector3.new(24,3.7,0.4),
	"FEEDS OFF / RODS SAFE",C.black,Enum.NormalId.Back,68)
-- In-world side diagnostics, lamp matrices, colored ceiling ribbons.
local matrixLamps={}
local ceilingBulbs={}
local floorFloods={}
local waveformBars={}
local wallScreenLabels={}
for _,side in ipairs({-1,1}) do
	local wallCF=CFrame.lookAt(Vector3.new(side*60.58,57,112),
		Vector3.new(0,57,112))
	part(gallery,"SIDE_BLACK_STATUS_CONSOLE",wallCF,
		Vector3.new(29,27,0.45),C.black,Enum.Material.Metal)
	local screen=part(gallery,"SIDE_SCROLLING_OPERATIONAL_SCREEN",
		wallCF*CFrame.new(side==-1 and -4.5 or 0,
			side==-1 and -4.4 or -8,-0.39),
		side==-1 and Vector3.new(18,10.8,0.16)
			or Vector3.new(25,8.5,0.16),
		C.black,Enum.Material.SmoothPlastic)
	local label=caption(screen,Enum.NormalId.Front,
		"CORE COLD\nTEMP 0026C\nPWR  000%\nFLOW 050%",
		68,C.ivory,Vector2.new(side==-1 and 580 or 660,345))
	label.TextScaled=false;label.TextWrapped=false
	label.Font=Enum.Font.GothamBold
	label.TextStrokeTransparency=0.72
	label.TextXAlignment=Enum.TextXAlignment.Left
	label.TextYAlignment=Enum.TextYAlignment.Center
	label.Size=UDim2.fromScale(0.93,0.93)
	label.Position=UDim2.fromScale(0.04,0.06)
	wallScreenLabels[side]=label
	if side==-1 then
		screen:SetAttribute("Role","MAIN_SYSTEMS")
		-- Reference's prominent THREE red lamp banks sit ABOVE the
		-- monitor; a small colored key matrix sits BESIDE it, not across
		-- the entire upper wall like the V1 screenshot.
		for bank=0,2 do
			local bankCF=wallCF*CFrame.new(-9.3+bank*9.25,
				11.15,-0.43)
			part(gallery,"TRIPLE_RED_HAZARD_BANK_HOUSING",
				bankCF,Vector3.new(7.7,3.2,0.18),
				C.frame,Enum.Material.Metal)
			for row=0,1 do
				for col=0,4 do
					part(gallery,"RED_HAZARD_BANK_DIODE",
						bankCF*CFrame.new(-2.87+col*1.4,
							0.72-row*1.39,-0.14),
						Vector3.new(0.66,0.44,0.12),
						C.red,Enum.Material.Neon,0.08)
				end
			end
		end
		for row=1,5 do
			for col=1,5 do
				local cc=wallCF*CFrame.new(5.45+(col-1)*1.72,
					-0.1-(row-1)*2.2,-0.52)
				local tint=(row+col)%5==0 and C.amber
					or (row*2+col)%3==0 and C.ruby or C.azure
				local cell=part(gallery,
					"LEFT_DIAGNOSTIC_COMPACT_COLOR_MATRIX",
					cc,Vector3.new(1.15,1.15,0.13),
					tint,Enum.Material.Neon,0.64)
				matrixLamps[#matrixLamps+1]={part=cell,row=row,
					col=col,side=side,normal=tint}
			end
		end
	else
		screen:SetAttribute("Role","SERVICE_SYSTEMS")
		for row=1,5 do
			for col=1,12 do
				local cc=wallCF*CFrame.new(-13+(col-1)*2.35,
					11.0-(row-1)*2.62,-0.43)
				local tint=(row+col)%6==0 and C.orange
					or (row+col)%3==0 and C.violet or C.azure
				local cell=part(gallery,"LIVE_STATUS_LED_CELL",
					cc,Vector3.new(1.36,0.92,0.13),
					tint,Enum.Material.Neon,0.63)
				matrixLamps[#matrixLamps+1]={part=cell,row=row,
					col=col,side=side,normal=tint}
			end
		end
	end
	for n=0,5 do
		local base=wallCF*CFrame.new(-11+n*4.5,-14.25,-0.36)
		local bar=part(gallery,"ALIVE_OSCILLOSCOPE_BAR",
			base,Vector3.new(0.62,2.8,0.18),
			C.mint,Enum.Material.Neon,0.58)
		waveformBars[#waveformBars+1]={part=bar,home=base,n=n,side=side}
	end
	for n=0,8 do
		local z=99+n*7.1
		beam(gallery,"CEILING_EXPOSED_CABLE_CONDUIT",
			Vector3.new(side*(31+n%3*6),78.9,z),
			Vector3.new(side*(31+n%3*6),78.9,z+6.3),
			0.3,C.charcoal,Enum.Material.Metal)
	end
end
for n=0,27 do
	local x=-53+(n%14)*8.1
	local z=n<14 and 100 or 155
	local tint=n%7==0 and C.magenta or n%5==0 and C.amber
		or n%3==0 and C.mint or C.azure
	local housing=box(gallery,"TINY_CEILING_SIGNAL_BULB",
		Vector3.new(x,78.8,z),Vector3.new(0.85,0.36,0.7),
		tint,Enum.Material.Neon,0.62)
	local glow=n%5==0 and lamp(housing,tint,0.13,17) or nil
	ceilingBulbs[#ceilingBulbs+1]={part=housing,point=glow,
		index=n,normal=tint}
end
-- Colored emergency/festival signal chain visible in the reference.
-- Small separate PointLights tint nearby metal; the control room stays ivory.
for _,side in ipairs({-1,1}) do
	for n=0,16 do
		local z=99+n*3.6
		local palette={C.magenta,C.amber,C.mint,C.azure,C.red,C.violet}
		local hue=palette[(n*2+(side==1 and 3 or 0))%#palette+1]
		beam(gallery,"CEILING_BULB_HANGING_CABLE",
			Vector3.new(side*58.5,79.45,z),
			Vector3.new(side*58.5,77.25,z),
			0.09,C.charcoal,Enum.Material.Metal)
		local globe=ball(gallery,"MULTICOLOR_CAGED_SIGNAL_BULB",
			Vector3.new(side*58.5,76.7,z),0.60,
			hue,Enum.Material.Neon,0.05)
		if n%2==0 then lamp(globe,hue,0.62,20) end
	end
end
for n=0,10 do
	local x=-50+n*10
	local marker=box(gallery,"RECESSED_FLOOR_RED_WARNING_RAIL",
		Vector3.new(x,29.1,96.8),Vector3.new(1.3,0.18,0.42),
		C.ruby,Enum.Material.Neon,0.62)
	floorFloods[#floorFloods+1]={body=marker,
		point=lamp(marker,C.warm,0.07,22),index=n}
end
for n=-5,5 do
	beam(gallery,"OVERHEAD_CEILING_CROSSBRACE",
		Vector3.new(n*10.8,79.4,95),
		Vector3.new(n*10.8,79.4,160),
		n%3==0 and 0.63 or 0.19,C.slate,Enum.Material.Metal)
end
local roomFillLights={}
for _,point in ipairs({
	Vector3.new(-44,74,130),Vector3.new(-15,74,143),
	Vector3.new(17,74,143),Vector3.new(45,74,130),
	Vector3.new(-46,60,105),Vector3.new(-14,64,112),
	Vector3.new(14,64,112),Vector3.new(46,60,105),
	}) do
	local anchor=ball(gallery,"HIDDEN_SOFT_WARM_AREA_LIGHT_ANCHOR",
		point,0.18,C.ivory,Enum.Material.SmoothPlastic,1)
	roomFillLights[#roomFillLights+1]=lamp(anchor,C.ivory,1.12,66)
end
local alarmFixtures={}
local bigLampBezel=box(gallery,"CENTRAL_RED_FRAMED_STATUS_LIGHT",
	Vector3.new(0,79.05,120),Vector3.new(46,1.10,6.2),
	C.ruby,Enum.Material.Metal)
local bigLampDiffuser=box(gallery,"DIFFUSE_IVORY_FLUORESCENT",
	Vector3.new(0,79.50,120),Vector3.new(43.5,0.38,5.1),
	C.porcelain,Enum.Material.SmoothPlastic,0.08)
local bigLampPoint=lamp(bigLampDiffuser,C.warm,0.49,36)
for _,p in ipairs({-45,-26,-8,8,26,45}) do
	local blockLight=box(gallery,"SUSPENDED_RUST_RED_HAZARD_FRAME",
		Vector3.new(p,79.8,112),Vector3.new(9.1,1.3,2.1),
		C.frame,Enum.Material.Metal)
	local shade=box(gallery,"WARM_RED_LAMP_DIFFUSER",
		blockLight.Position-Vector3.new(0,0.78,0),
		Vector3.new(8.4,0.21,1.6),C.ivory,
		Enum.Material.Neon,0.19)
	alarmFixtures[#alarmFixtures+1]={body=shade,
		light=lamp(shade,C.warm,0.18,21),index=#alarmFixtures+1}
end
-- ================================================================
-- 3. FACE-ON SIX-EMITTER WHITE STAR; exact focus of the 144p reference.
-- ================================================================
-- A DARK, layered cobalt wall, not a 90%-transparent neon sheet in
-- front of the rust-red wall. Screenshot reference: blue/black occupies
-- the entire chamber; white light is confined to the actual small star.
local plasmaBackdrop=box(machine,"OPAQUE_DEEP_COBALT_CHAMBER_BACK",
	Vector3.new(0,54,-57),Vector3.new(79,84,1.5),
	Color3.fromRGB(13,31,91),Enum.Material.SmoothPlastic,0.02)
plasmaBackdrop.CastShadow=false
-- Only the old OUTER framing slabs are retinted blue-grey steel to match
-- 360p cold imagery. The separately APPROVED brown PBR mesh rear bulkhead
-- and its two grille banks are untouched (no silent model replacement).
for _,side in ipairs({-1,1}) do
	local x=side*51.5
	box(chamber,"OUTER_BLUE_GREY_FACETED_BACKPLATE",
		Vector3.new(x,55,-59.0),Vector3.new(24.4,71,1.0),
		Color3.fromRGB(87,101,128),Enum.Material.Metal)
	box(chamber,"DEEP_REACTOR_ACCESS_BAY",
		Vector3.new(x,53,-58.1),Vector3.new(17.8,31,0.6),
		C.charcoal,Enum.Material.Metal)
	local plaque=box(chamber,"CONTAINMENT_DANGER_MARKER",
		Vector3.new(x,54,-57.6),Vector3.new(13.8,7.4,0.25),
		C.black,Enum.Material.Metal)
	local sign=caption(plaque,Enum.NormalId.Back,
		"CONTAINMENT  /  04",49,C.ivory,Vector2.new(640,210))
	sign.TextScaled=true;sign.TextWrapped=false
	for row=0,8 do
		local y=17+row*9.4
		beam(chamber,"ARMOR_HAZARD_DIAGONAL",
			Vector3.new(x-10.0,y,-57.51),
			Vector3.new(x-5.5,y+4.1,-57.51),
			0.62,row%2==0 and C.amber or C.orange,
			Enum.Material.Neon,0.11)
		beam(chamber,"ARMOR_VERTICAL_TRIM",
			Vector3.new(x+10.7,y,-57.4),
			Vector3.new(x+10.7,y+7.5,-57.4),
			0.23,C.trim,Enum.Material.Metal)
	end
end
-- Low, blue wall wash is addressable by the chamber-only dark transition.
-- The gallery's physically separate control lights stay on.
local chamberWashLights={}
for _,x in ipairs({-40,0,40}) do
	local glow=ball(machine,"BACKDROP_BLUE_WASH_INVISIBLE",
		Vector3.new(x,55,-48),0.16,C.azure,
		Enum.Material.SmoothPlastic,1)
	chamberWashLights[#chamberWashLights+1]=
		lamp(glow,x==0 and C.cobalt or C.azure,1.25,67)
end
local remoteNebula={}
local chamberMist={}
for n=1,12 do
	local a=n*TAU/12
	local center=CORE+Vector3.new(math.cos(a)*38,
		math.sin(a)*29,-28-(n%3)*8)
	local anchor=ball(machine,"VOLUMETRIC_INDIGO_MIST_ANCHOR",
		center,0.07,C.black,Enum.Material.SmoothPlastic,1)
	anchor.CanQuery=false
	local smoke=particles(anchor,"BLUE_AND_PURPLE_MOVING_PLASMA",
		SMOKE,8,n%3==0 and C.violet or C.nebula,
		7.5,17.5,2.5)
	smoke.Lifetime=NumberRange.new(2.8,5.8)
	smoke.SpreadAngle=Vector2.new(180,180)
	smoke.Acceleration=Vector3.new(0,2.7,0)
	smoke.Transparency=NumberSequence.new({
		NumberSequenceKeypoint.new(0,0.91),
		NumberSequenceKeypoint.new(0.31,0.59),
		NumberSequenceKeypoint.new(1,1)})
	smoke.LightEmission=0.22
	smoke.Enabled=true
	chamberMist[#chamberMist+1]=smoke
end
for n=1,62 do
	local x=rng:NextNumber(-57,57)
	local y=rng:NextNumber(14,92)
	local z=-55.95+rng:NextNumber(0,0.64)
	local blob=ball(machine,"INDIGO_REACTOR_CLOUD_"..n,
		Vector3.new(x,y,z),1,C.nebula,
		Enum.Material.Neon,rng:NextNumber(0.72,0.88))
	blob.Size=Vector3.new(rng:NextNumber(5,20),
		rng:NextNumber(2,9),rng:NextNumber(0.13,0.32))
	blob.Color=n%9==0 and C.violet
		or n%3==0 and C.cobalt or C.nebula
	blob.CastShadow=false
	remoteNebula[#remoteNebula+1]=blob
end
for n=1,105 do
	local a=Vector3.new(rng:NextNumber(-57,57),
		rng:NextNumber(16,91),-54.9)
	local b=a+Vector3.new(rng:NextNumber(-4,4),
		rng:NextNumber(-2,2),0)
	local vein=beam(machine,"WISPY_BLUE_ELECTRICAL_CRACKLE",
		a,b,rng:NextNumber(0.08,0.24),
		n%11==0 and C.magenta or C.azure,
		Enum.Material.Neon,0.61)
	vein.CastShadow=false
end
for n=1,90 do
	local mote=ball(machine,"DISTANT_BLUE_FLECK",
		Vector3.new(rng:NextNumber(-55,55),
			rng:NextNumber(18,88),-54.3),
		rng:NextNumber(0.065,0.21),
		n%11==0 and C.magenta or C.azure,
		Enum.Material.Neon,rng:NextNumber(0.38,0.75))
	mote.CastShadow=false
end
for _,x in ipairs({-46,-15,15,46}) do
	local lampBody=ball(machine,"BACKDROP_INDIGO_RECESS_LIGHT",
		Vector3.new(x,49,-54.9),0.18,C.navy,
		Enum.Material.SmoothPlastic,1)
	lamp(lampBody,C.cobalt,0.28,29)
end
for _,side in ipairs({-1,1}) do
	for n=0,6 do
		local x=side*(51+n*3.2)
		beam(machine,"REACTOR_REAR_BLUE_VANE",
			Vector3.new(x,26,-55),Vector3.new(x,89,-55),
			0.33,n%2==0 and C.azure or C.violet,
			Enum.Material.Neon,0.54)
	end
end
for _,r in ipairs({20,28,39,52}) do
	circleXZ(machine,"CORE_FLOOR_HEAT_OUTLINE_"..r,
		Vector3.new(0,0.38,0),r,48,
		r==39 and 0.38 or 0.2,r==39 and C.amber or C.cobalt,
		Enum.Material.Neon,r==39 and 0.13 or 0.33)
end
cylY(machine,"HEAVY_REACTOR_FOUNDATION",
	Vector3.new(0,6,0),20,11,C.trim,
	Enum.Material.DiamondPlate,0,true)
cylY(machine,"FOUNDATION_INDUCTION_RING",
	Vector3.new(0,12.3,0),22.6,0.65,C.azure,
	Enum.Material.Neon,0.22)
for _,sy in ipairs({20,87}) do
	for n=0,8 do
		local a=n*TAU/9
		local x=math.cos(a)*34;local z=math.sin(a)*18-23
		tube(machine,"OVERSIZED_CORE_SUSPENSION_PISTON",
			Vector3.new(x,sy, z),
			Vector3.new(x*1.21,sy+(sy>53 and 11 or -12),z*1.4),
			0.82,C.trim,Enum.Material.Metal)
	end
end
local coreRoot=ball(machine,"INNER_HEART_VIOLET_PLASMA",CORE,
	7.8,C.violet,Enum.Material.Neon,0.68)
local whiteStar=ball(machine,"INCANDESCENT_VISIBLE_STAR",
	CORE+Vector3.new(0,0,35),5.6,C.white,
	Enum.Material.Neon,0.04)
local pinkCrown=ball(machine,"MAGENTA_PHOTOSPHERE",
	CORE+Vector3.new(0,0,27),12.5,C.magenta,
	Enum.Material.Neon,0.90)
local paleHalo=ball(machine,"SOFT_WHITE_CONTAINMENT_HALO",
	CORE+Vector3.new(0,0,25),19,C.violet,
	Enum.Material.Neon,0.96)
local corona=ball(machine,"BACKLIT_WHITE_PHOTOSPHERE_CORONA",
	CORE+Vector3.new(0,0,32),10.7,C.ivory,
	Enum.Material.Neon,0.89)
corona.CastShadow=false
local coreLamp=lamp(whiteStar,C.ivory,
	CFG.VISUAL.CORE_LIGHT_IDLE,CFG.VISUAL.CORE_LIGHT_RANGE)
local coreDust=particles(whiteStar,"SPARKS_IN_THE_PLASMA",
	SPARK,48,C.white,1.55,0.08,22)
coreDust.LightEmission=1
coreDust.SpreadAngle=Vector2.new(180,180)
coreDust.Enabled=false
local coreSmoke=particles(coreRoot,"BLUE_PLASMA_MIST",
	SMOKE,10,C.cobalt,2.7,12,4)
coreSmoke.LightEmission=0.28
coreSmoke.Color=ColorSequence.new(C.nebula,C.violet)
coreSmoke.Transparency=NumberSequence.new({
	NumberSequenceKeypoint.new(0,0.84),
	NumberSequenceKeypoint.new(0.38,0.58),
	NumberSequenceKeypoint.new(1,1)})
coreSmoke.Lifetime=NumberRange.new(2.3,4.4)
coreSmoke.Enabled=true
-- Radial tongues turn the central orb into a visible, irregular STAR
-- rather than a featureless glowing billiard ball. Entirely inactive in COLD.
local coreSpokes={}
for n=0,11 do
	local a=n*TAU/12
	local r=n%3==0 and 18.5 or 12.5
	local inside=CORE+Vector3.new(math.cos(a)*3,
		math.sin(a)*3,35)
	local outside=CORE+Vector3.new(math.cos(a)*r,
		math.sin(a)*r,34)
	local spike=beam(machine,"PHOTOSPHERE_WHITE_FUSION_TONGUE",
		inside,outside,n%3==0 and 2.1 or 0.86,
		C.white,Enum.Material.Neon,1)
	coreSpokes[#coreSpokes+1]=spike
	local aura=beam(machine,"PHOTOSPHERE_SOFT_IRIS_AURA",
		inside,outside,n%3==0 and 3.9 or 2.1,
		C.magenta,Enum.Material.Neon,1)
	coreSpokes[#coreSpokes+1]=aura
end
local fallingAsh=particles(coreRoot,"FALLOUT_FROM_CORE",
	SMOKE,82,C.charcoal,4.4,28,18)
fallingAsh.Lifetime=NumberRange.new(2.4,5.5)
fallingAsh.Enabled=false
for n=0,23 do
	local a=n*TAU/24
	local p=CORE+Vector3.new(math.cos(a)*16,math.sin(a)*16,18)
	local q=CORE+Vector3.new(math.cos(a+0.14)*19,
		math.sin(a+0.14)*19,16)
	beam(machine,"CHAMBER_CONTAINED_MICRO_ARC",p,q,
		n%6==0 and 0.18 or 0.12,
		n%6==0 and C.white or C.violet,
		Enum.Material.Neon,n%6==0 and 0.94 or 0.99)
end

-- Reference silhouette: vertical TOP and BOTTOM, LEFT and RIGHT,
-- two inward-looking LOWER DIAGONAL heads. Never replace with evenly
-- spaced X/Z torches (they would disappear from the observation window).
local emitterSites={
	{tag="UPPER",vec=Vector3.new(0,1,0)},
	{tag="LEFT",vec=Vector3.new(-1,0,0)},
	{tag="RIGHT",vec=Vector3.new(1,0,0)},
	{tag="LOWER_LEFT",vec=Vector3.new(-0.72,-0.70,0)},
	{tag="LOWER_RIGHT",vec=Vector3.new(0.72,-0.70,0)},
	{tag="LOWER",vec=Vector3.new(0,-1,0)},
}
local function opticalJet(parent,name,a,b,width,color,alpha)
	local a0=ball(parent,name.."_START",a,0.06,C.black,
		Enum.Material.SmoothPlastic,1)
	local a1=ball(parent,name.."_END",b,0.06,C.black,
		Enum.Material.SmoothPlastic,1)
	a0.CanQuery=false;a1.CanQuery=false
	local pin0=Instance.new("Attachment");pin0.Parent=a0
	local pin1=Instance.new("Attachment");pin1.Parent=a1
	local jet=Instance.new("Beam")
	jet.Name=name;jet.Attachment0=pin0;jet.Attachment1=pin1
	jet.Width0=width*WORLD_SCALE
	jet.Width1=width*0.67*WORLD_SCALE
	jet.Segments=16;jet.FaceCamera=true
	jet.LightEmission=1
	jet.Transparency=NumberSequence.new(alpha)
	jet.Color=ColorSequence.new(color,color)
	jet.Parent=parent
	return jet
end
local emitters={}
for i,site in ipairs(emitterSites) do
	local axis=site.vec.Unit
	local function radial(r,z)
		return CORE+axis*(r*WORLD_SCALE)+Vector3.new(0,0,z or 15)
	end
	local bareMetal={}
	local mainBarrel=tube(machine,"PROJECTOR_"..site.tag.."_MAIN_SHAFT",
		radial(36,10),radial(60,10),6.2,C.slate,
		Enum.Material.Metal)
	bareMetal[#bareMetal+1]=mainBarrel
	bareMetal[#bareMetal+1]=tube(machine,
		"PROJECTOR_"..site.tag.."_FRONT_SLEEVE",
		radial(29,14),radial(40,14),4.85,C.silver,
		Enum.Material.Metal)
	bareMetal[#bareMetal+1]=tube(machine,
		"PROJECTOR_"..site.tag.."_REAR_COLLAR",
		radial(57,11),radial(64,11),6.55,C.slate,
		Enum.Material.Metal)
	for _,v in ipairs({36,43,50,57}) do
		bareMetal[#bareMetal+1]=tube(machine,
			"PROJECTOR_"..site.tag.."_CHROME_COLLAR",
			radial(v-0.38,14),radial(v+0.38,14),
			v==36 and 5.3 or 6.65,C.silver,Enum.Material.Metal)
		bareMetal[#bareMetal+1]=tube(machine,
			"PROJECTOR_"..site.tag.."_GLOWING_COOLANT_LOOP",
			radial(v+0.58,14),radial(v+0.93,14),
			v==36 and 5.25 or 6.7,
			v==50 and C.violet or C.azure,
			Enum.Material.Neon,0.48)
		for bolt=0,3 do
			local angle=bolt*TAU/4
			local lateral=Vector3.new(-axis.Y,axis.X,0)
			local rim=radial(v,16)+lateral*math.cos(angle)*5.4
				+Vector3.new(0,0,math.sin(angle)*1.5)
			bareMetal[#bareMetal+1]=ball(machine,
				"PROJECTOR_SPRING_BOLT",rim,0.38,
				C.silver,Enum.Material.Metal)
		end
	end
	for side=-1,1,2 do
		local lateral=Vector3.new(-axis.Y,axis.X,0)
		bareMetal[#bareMetal+1]=beam(machine,
			"PROJECTOR_TWIN_POWER_CONDUITS",
			radial(43,9)+lateral*side*3.7,
			radial(58,9)+lateral*side*3.7,0.42,
			C.azure,Enum.Material.Neon,0.48)
	end
	-- A layered, hollow-looking machined projector, NOT a giant white orb.
	-- Front metallic cylinder can be torn free during the scripted failure.
	local nozzle=tube(machine,
		"PROJECTOR_"..site.tag.."_BREAKABLE_MUZZLE_SLEEVE",
		radial(27.2,18),radial(31.4,18),5.35,
		C.silver,Enum.Material.Metal)
	local blackBore=tube(machine,
		"PROJECTOR_"..site.tag.."_DARK_INNER_BORE",
		radial(25.7,18.1),radial(27.3,18.1),3.15,
		C.black,Enum.Material.SmoothPlastic)
	bareMetal[#bareMetal+1]=blackBore
	local focusRing=tube(machine,
		"PROJECTOR_"..site.tag.."_CYAN_IRIS_CHANNEL",
		radial(26.0,21.9),radial(26.35,21.9),4.3,
		C.azure,Enum.Material.Neon,0.57)
	bareMetal[#bareMetal+1]=focusRing
	local lens=ball(machine,"PROJECTOR_"..site.tag.."_BLUE_FOCUS",
		radial(25.8,21.7),2.05,C.azure,Enum.Material.Neon,0.20)
	local iris={}
	for edge=0,11 do
		local a=edge*TAU/12;local b=(edge+1)*TAU/12
		local center=radial(29,22)
		local p=center+Vector3.new(math.cos(a)*5.25,
			math.sin(a)*4.45,0)
		local q=center+Vector3.new(math.cos(b)*5.25,
			math.sin(b)*5.25,0)
		iris[#iris+1]=beam(machine,
			"PROJECTOR_DETACHABLE_TEETH_"..site.tag,
			p,q,0.48,C.white,Enum.Material.Metal)
	end
	local a=CORE+axis*(6*WORLD_SCALE)+Vector3.new(0,0,27)
	local b=CORE+axis*(28*WORLD_SCALE)+Vector3.new(0,0,27)
	local glow=beam(machine,"SIX_ARMS_"..site.tag.."_WIDE_HALO",
		a,b,5.3,C.violet,Enum.Material.Neon,1)
	local ray=beam(machine,"SIX_ARMS_"..site.tag.."_PINK_BEAM",
		a,b,3.05,C.magenta,Enum.Material.Neon,1)
	local filament=beam(machine,"SIX_ARMS_"..site.tag.."_WHITE_HOT_FILAMENT",
		a,b,1.55,C.ivory,Enum.Material.Neon,1)
	local softOptic=opticalJet(machine,
		"PROJECTOR_"..site.tag.."_BLUE_RIBBON_BEAM",
		a+Vector3.new(0,0,0.4),b,4.6,C.cyan,0.77)
	local hotOptic=opticalJet(machine,
		"PROJECTOR_"..site.tag.."_PHOTONIC_WHITE_BEAM",
		a+Vector3.new(0,0,0.7),b,2.45,C.white,0.32)
	-- FAZ4.1: R5 sahte turuncu yanik kuresi (MOLTEN_EMITTER_DAMAGE) ve 2B
	-- kivilcim yagmuru kaldirildi. Gercek ariza fizigi Faz 4.3'te GLB
	-- kafalar uzerinde kurulacak; e.broken durumu aynen korunuyor.
	local scorch=nil
	local spit=nil
	local lightSource=lamp(lens,C.azure,0.08,36)
	local focusSparks=particles(lens,"EACH_LENS_FIRES_IN_ORDER",
		SPARK,0,C.cyan,0.72,0.04,13)
	focusSparks.SpreadAngle=Vector2.new(180,180)
	focusSparks.LightEmission=1
	for _,distance in ipairs({40,48,55}) do
		local rib=tube(machine,"PROJECTOR_RIVETED_MACHINED_CUFF",
			radial(distance,14),radial(distance+0.52,14),
			6.8,C.silver,Enum.Material.Metal)
		bareMetal[#bareMetal+1]=rib
		for _,side in ipairs({-1,1}) do
			local offset=Vector3.new(-axis.Y,axis.X,0)*side*6.35
			bareMetal[#bareMetal+1]=ball(machine,
				"PROJECTOR_SHOULDER_RIVET",
				radial(distance+0.27,14)+offset,
				0.37,C.charcoal,Enum.Material.Metal)
		end
	end
	local originalBody={}
	for _,piece in ipairs(bareMetal) do
		originalBody[piece]=piece.Color
	end
	emitters[i]={id=i,tag=site.tag,axis=axis,body=bareMetal,
		originalBody=originalBody,
		nozzle=nozzle,nozzleHome=nozzle.CFrame,lens=lens,
		iris=iris,light=lightSource,
		ray=ray,glow=glow,filament=filament,
			hotOptic=hotOptic,softOptic=softOptic,scorch=scorch,
		sparks=spit,focusSparks=focusSparks,broken=false}
	hotOptic.Enabled=false;softOptic.Enabled=false
end

local frontBands={}
for bandNum,r in ipairs({22.5,34.2,43.8}) do
	local band={radius=r,speed=(bandNum%2==0 and -1 or 1)*
		(0.16+bandNum*0.05),parts={},depth=19-bandNum*2}
	for seg=0,47 do
		local a=seg*TAU/48;local b=(seg+1)*TAU/48
		local p=Vector3.new(math.cos(a)*r,math.sin(a)*r,0)
		local q=Vector3.new(math.cos(b)*r,math.sin(b)*r,0)
		local shape=CFrame.lookAt((p+q)/2,q)
		local color=seg%6==0 and C.silver
			or bandNum==2 and C.azure or C.violet
		local section=part(machine,"SHEARABLE_ORBITAL_RING_"..
			bandNum.."_"..seg,
			CFrame.new(CORE+Vector3.new(0,0,band.depth))*shape,
			Vector3.new(seg%6==0 and 0.68 or 0.29,
				seg%6==0 and 0.68 or 0.29,
				(q-p).Magnitude+0.06),color,
			seg%6==0 and Enum.Material.Metal or Enum.Material.Neon,
			seg%6==0 and 0 or 0.62)
		band.parts[#band.parts+1]={part=section,home=shape,
			broken=false,color=color,alpha=section.Transparency}
	end
	frontBands[#frontBands+1]=band
end
-- Decorative storm arcs are moved continuously in the actual X/Y plane.
local dynamicArcs={}
for i=1,34 do
	local arc=beam(machine,"CENTER_PLASMA_ARC_"..i,
		CORE+Vector3.new(2,0,28),
		CORE+Vector3.new(17,5,29),
		i%5==0 and 0.52 or 0.24,
		i%9==0 and C.white or C.magenta,
		Enum.Material.Neon,1)
	dynamicArcs[#dynamicArcs+1]=arc
end
local rods={}
for i=0,15 do
	local a=i*TAU/16
	local x=math.cos(a)*15.6
	local z=math.sin(a)*13-5
	local body=box(machine,"HYDRAULIC_SCRAM_CONTROL_ROD",
		Vector3.new(x,97,z),Vector3.new(0.95,24,0.95),
		C.charcoal,Enum.Material.Metal)
	local tip=ball(machine,"CONTROL_ROD_VISIBLE_TIP",
		Vector3.new(x,84,z),0.75,C.azure,Enum.Material.Neon)
	rods[#rods+1]={body=body,tip=tip,x=x,z=z}
end
-- Real peripheral failures; they are supporting detail, never the main shot.
local coolantLines={}
for i=0,9 do
	local angle=(i+0.5)*TAU/10
	local x=math.cos(angle)*78;local z=math.sin(angle)*69
	-- No reservoir or hose may stand dead-center in the camera window.
	if math.abs(x)<43 then x=(x<0 and -1 or 1)*43 end
	local tank=cylY(machine,"COOLANT_RESERVOIR_"..i,
		Vector3.new(x,17,z),5.8,30,C.trim,
		Enum.Material.Metal,0,true)
	cylY(machine,"RESERVOIR_CYAN_GAUGE",
		Vector3.new(x,19,z),6.04,24,C.azure,
		Enum.Material.SmoothPlastic,0.86)
	local fill=cylY(machine,"ACTIVE_BLUE_WATER",
		Vector3.new(x,10,z),5.55,16,C.cobalt,
		Enum.Material.Neon,0.61)
	for _,y in ipairs({5,27}) do
		cylY(machine,"TANK_PRESSURE_CLAMP",Vector3.new(x,y,z),
			6.3,0.55,C.silver,Enum.Material.Metal)
	end
	local from=Vector3.new(x,39,z)
	local to=Vector3.new(x*0.86,75,z*0.78)
	local pipe=tube(machine,"BREAKABLE_BLUE_FEED_PIPE_"..i,
		from,to,1.45,C.trim,Enum.Material.Metal,0,true)
	-- FAZ4.1: sahte boru agzi kuresi (PIPE_RUPTURE_LIP) + 2B jet/buhar
	-- kaldirildi. Kopma durumu (broken/leaking + damagedPipes) korunuyor;
	-- gercek 3B yirtik + sizinti Faz 4.2 (M13) ile gelecek.
	local mouth,spray,steam=nil,nil,nil
	coolantLines[i+1]={pipe=pipe,mouth=mouth,spray=spray,
		steam=steam,fill=fill,broken=false,leaking=false,
		x=x,z=z}
end
local viewportFeeds={}
for _,side in ipairs({-1,1}) do
	local x=side*45.7
	local pipe=tube(machine,"FRONT_VIEWPORT_COOLANT_RISER",
		Vector3.new(x,26,63),Vector3.new(x,72,63),0.78,
		C.silver,Enum.Material.Metal)
	-- FAZ4.1: sahte yara kuresi (RISER_PRESSURE_RUPTURE) + 2B jet/buhar kaldirildi.
	local scar,jet,vapor=nil,nil,nil
	viewportFeeds[#viewportFeeds+1]={pipe=pipe,scar=scar,
		jet=jet,vapor=vapor}
	for _,y in ipairs({31,41,62,70}) do
		tube(machine,"FRONT_RISER_CHROME_BAND",
			Vector3.new(x,y-0.25,63),
			Vector3.new(x,y+0.25,63),1.04,
			C.trim,Enum.Material.Metal)
	end
end
-- ================================================================
-- 4. ONLY REACTOR-RELATED CORRIDORS, CARD BAYS AND A SURVIVAL BUNKER.
-- ================================================================
local sideDoors={}
local cardBays={}
for _,side in ipairs({-1,1}) do
	local x=side*84.6
	box(service,"REACTOR_SERVICE_HALL_FLOOR",
		Vector3.new(x,22.12,143),Vector3.new(43,3.5,109),
		C.porcelain,Enum.Material.SmoothPlastic,0,true)
	box(service,"CONTROL_ROOM_TO_HALL_THRESHOLD",
		Vector3.new(side*62.5,22.42,132),Vector3.new(10,3.5,15),
		C.silver,Enum.Material.Metal,0,true)
	box(service,"REACTOR_HALL_CEILING",
		Vector3.new(x,68,143),Vector3.new(45,2.2,109),
		C.slate,Enum.Material.Metal,0,true)
	box(service,"REACTOR_HALL_OUTER_WALL",
		Vector3.new(side*107,45,143),Vector3.new(2,46,109),
		C.porcelain,Enum.Material.Metal,0,true)
	box(service,"REACTOR_HALL_BACK_WALL",
		Vector3.new(x,45,198),Vector3.new(45,46,2),
		C.porcelain,Enum.Material.Metal,0,true)
	box(service,"REACTOR_HALL_FRONT_WALL",
		Vector3.new(x,45,88),Vector3.new(45,46,2),
		C.porcelain,Enum.Material.Metal,0,true)
	box(service,"REACTOR_HALL_INNER_BACK_WALL",
		Vector3.new(side*62,45,181),Vector3.new(2,46,35),
		C.porcelain,Enum.Material.Metal,0,true)
	local leaf=box(service,"AUTOMATIC_SIDE_AIRLOCK_LEAF",
		Vector3.new(side*62,34,132),Vector3.new(1.2,19,14),
		C.trim,Enum.Material.Metal,0,true)
	local strip=box(service,"AIRLOCK_MOVING_STATUS_LIGHT",
		Vector3.new(side*61.25,35,132),
		Vector3.new(0.15,1.0,12),C.mint,Enum.Material.Neon)
	local folderDoor={leaf=leaf,strip=strip,home=leaf.CFrame,
		stripHome=strip.CFrame,open=false,lastNear=0,side=side}
	sideDoors[#sideDoors+1]=folderDoor
	for row=0,15 do
		local z=95+row*6.5
		beam(service,"SERVICE_HALL_CABLE_CHANNEL",
			Vector3.new(side*104,27,z),
			Vector3.new(side*104,58,z),
			0.13,row%3==0 and C.orange or C.trim,
			row%3==0 and Enum.Material.Neon or Enum.Material.Metal,
			0.12)
	end
	for n=0,10 do
		local z=96+n*9.6
		local bulb=box(service,"SERVICE_HALL_FUNCTIONAL_LIGHT",
			Vector3.new(x,66,z),Vector3.new(6.6,0.4,2.1),
			C.white,Enum.Material.Neon,0.11)
		if n%3==0 then lamp(bulb,C.white,0.85,36) end
	end
	for n=1,3 do
		local z=109+(n-1)*35
		local pc=Vector3.new(side*85,26.6,z)
		local plinth=box(service,"CARD_BAY_SOLID_PEDESTAL",
			pc-Vector3.new(0,1.4,0),Vector3.new(12,3.2,8),
			C.trim,Enum.Material.Metal,0,true)
		local top=box(service,"CARD_BAY_BEVELED_BEZEL",
			pc+Vector3.new(0,0.3,0),Vector3.new(11.6,0.36,7.6),
			C.charcoal,Enum.Material.Metal)
		local lip=box(service,"CARD_BAY_NEON_PEDESTAL_EDGE",
			pc+Vector3.new(0,0.58,0),Vector3.new(10.9,0.12,6.8),
			C.azure,Enum.Material.Neon,0.7)
		local card=part(service,"PICKUP_REACTOR_AUTH_CARD",
			CFrame.new(pc+Vector3.new(0,1.3,0))
				*CFrame.Angles(0,0,math.rad(18)),
			Vector3.new(4.3,0.21,2.5),
			C.mint,Enum.Material.Neon,1)
		local badge=box(service,"PHYSICAL_CARD_FACE",
			card.Position+Vector3.new(0,0.13,0),
			Vector3.new(3.7,0.07,2.12),C.black,
			Enum.Material.SmoothPlastic,1)
		badge.CanQuery=false -- decorative face must not eat card clicks.
		local cardDetector=Instance.new("ClickDetector")
		cardDetector.MaxActivationDistance=9
		cardDetector.Parent=card
		local sign=box(service,"CARD_BAY_HARDWARE_LABEL",
			pc+Vector3.new(0,3,-2.7),
			Vector3.new(10.4,1.7,0.24),C.black,Enum.Material.Metal)
		caption(sign,Enum.NormalId.Front,
			"REACTOR AUTHORIZATION BAY "..n,41,C.white,
			Vector2.new(920,200))
		cardBays[#cardBays+1]={location=pc,side=side,
			plinth=plinth,bezel=top,edge=lip,card=card,
			face=badge,click=cardDetector,used=false,slot=nil}
	end
end
local bunkerFloor=box(service,"EMERGENCY_BUNKER_HARD_FLOOR",
	Vector3.new(0,22.16,199.6),Vector3.new(50,3.4,72.8),
	C.silver,Enum.Material.DiamondPlate,0,true)
box(service,"BUNKER_LOW_ROOF",Vector3.new(0,52,199),
	Vector3.new(51,3,73),C.trim,Enum.Material.Metal,0,true)
for _,side in ipairs({-1,1}) do
	box(service,"BUNKER_METER_THICK_WALL",
		Vector3.new(side*26,37,199),Vector3.new(3,30,73),
		C.trim,Enum.Material.Metal,0,true)
	beam(service,"FOSFOR_ESCAPE_STRIPE",
		Vector3.new(side*22,24.25,165),
		Vector3.new(side*22,24.25,228),
		0.28,C.mint,Enum.Material.Neon)
	for n=1,4 do
		cylY(service,"BUNKER_OXYGEN_AND_POWER_TANK",
			Vector3.new(side*20,30,174+n*10),2,10,
			C.silver,Enum.Material.Metal)
	end
end
box(service,"BUNKER_BACK_WALL",Vector3.new(0,38,235),
	Vector3.new(50,31,2.5),C.trim,Enum.Material.Metal,0,true)
for _,side in ipairs({-1,1}) do
	box(service,"BUNKER_FRONT_ARMOR_FIXED",
		Vector3.new(side*18,35,165.1),
		Vector3.new(17,25,2),C.trim,Enum.Material.Metal,0,true)
end
box(service,"BUNKER_ENTRY_HEADER",Vector3.new(0,49,165.1),
	Vector3.new(19,10,2.2),C.trim,Enum.Material.Metal,0,true)
local bunkerGate=box(service,"AUTO_SEAL_BUNKER_GATE",
	Vector3.new(0,59.5,165.1),Vector3.new(19,24,1.8),
	C.trim,Enum.Material.Metal)
local bunkerGateClosed=CFrame.new(0,36,165.1)
local bunkerGateOpen=bunkerGate.CFrame
local bunkerLamp=box(service,"BUNKER_INDICATOR",
	Vector3.new(0,48,165.1),Vector3.new(7.5,0.9,1.6),
	C.mint,Enum.Material.Neon)
lamp(bunkerLamp,C.mint,1.45,35)
for _,z in ipairs({180,197,214,227}) do
	local bar=box(service,"BUNKER_AUTO_CEILING_BATTERY",
		Vector3.new(0,48.9,z),Vector3.new(16,0.65,2.9),
		C.mint,Enum.Material.Neon,0.16)
	lamp(bar,C.mint,0.7,24)
end
local spawn=Instance.new("SpawnLocation")
spawn.Name="CORE_PROTOCOL_V2_DIAGONAL_REFERENCE_VIEW"
spawn.Size=Vector3.new(8,0.6,8)
spawn.CFrame=CFrame.new(-29,24.45,151)
spawn.Color=C.floor;spawn.Material=Enum.Material.Metal
spawn.Anchored=true;spawn.Neutral=true;spawn.Duration=0
spawn.Parent=gallery
for _,v in ipairs(Workspace:GetDescendants()) do
	if v:IsA("SpawnLocation") and v~=spawn then v.Enabled=false end
end

-- ================================================================
-- 5. MACHINED, ANIMATED, FULLY FUNCTIONAL CONTROL HARDWARE.
-- ================================================================
local workingControls={}
local function makeControl(name,kind,position,color,legend)
	-- V1 used 11.6x9.5-stud Neon-heavy stations. Seven of those consumed
	-- most of the user's actual screenshot. This assembly is 8x6.5 studs,
	-- predominantly steel/bakelite with ONLY a narrow status pip.
	local structure=folder(interfaces,name.."_FUNCTIONAL_STATION")
	local base=box(structure,"CNC_STEEL_BEVELED_PEDESTAL",
		position-Vector3.new(0,1.32,0),
		Vector3.new(7.95,2.0,6.5),C.trim,
		Enum.Material.Metal,0,true)
	local collar=box(structure,"BLACK_BAKELITE_SLOPED_CAP",
		position-Vector3.new(0,0.24,0),
		Vector3.new(7.56,0.32,6.06),C.charcoal,
		Enum.Material.Metal)
	local neon=box(structure,"THIN_WORKING_INDICATOR_RAIL",
		position+Vector3.new(0,-0.035,-0.7),
		Vector3.new(7.0,0.055,3.88),color,
		Enum.Material.Neon,0.84)
	for _,side in ipairs({-1,1}) do
		box(structure,"VISIBLE_METAL_SIDE_BOLT",
			position+Vector3.new(side*3.48,-0.04,-2.27),
			Vector3.new(0.27,0.11,0.27),C.silver,
			Enum.Material.Metal)
	end
	local rim=cylY(structure,"POLISHED_SWITCH_BEZEL",
		position+Vector3.new(0,0.15,-0.88),
		1.33,0.27,C.silver,Enum.Material.Metal)
	local innerRim=cylY(structure,"RECESSED_COLOR_SLEEVE",
		position+Vector3.new(0,0.33,-0.88),
		1.05,0.065,color,Enum.Material.Neon,0.7)
	local handle
	local rod=nil
	local tip=nil
	if kind=="lever" then
		local bottom=position+Vector3.new(0,0.39,-0.88)
		local top=bottom+Vector3.new(0,1.85,0)
		rod=beam(structure,"MOVING_STEEL_SHAFT",
			bottom,top,0.32,C.silver,Enum.Material.Metal)
		handle=ball(structure,"GRAB_AND_CLICK_THIS_LEVER",
			top,0.68,color,Enum.Material.SmoothPlastic)
		tip=ball(structure,"LEVER_COLORED_TIP",
			top+Vector3.new(0,0.43,0),0.23,color,
			Enum.Material.Neon,0.38)
		tip.CanQuery=false
	elseif kind=="dial" then
		handle=cylY(structure,"TACTILE_TURNING_COOLANT_DIAL",
			position+Vector3.new(0,0.46,-0.88),
			0.95,0.32,C.silver,Enum.Material.Metal)
		rod=beam(structure,"DIAL_MOVABLE_CYAN_POINTER",
			position+Vector3.new(0,0.68,-0.88),
			position+Vector3.new(0,0.68,-1.99),
			0.11,color,Enum.Material.Neon,0.24)
		rod.CanQuery=false -- Do not steal clicks from the working knob.
		innerRim:SetAttribute("WorkingDial",true)
	else
		handle=cylY(structure,"CLICKABLE_COLORED_STEEL_PUSHER",
			position+Vector3.new(0,0.47,-0.88),
			0.94,0.32,color,Enum.Material.SmoothPlastic)
		local ring=cylY(structure,"THIN_ILLUMINATED_BUTTON_RING",
			position+Vector3.new(0,0.64,-0.88),
			0.74,0.045,color,Enum.Material.Neon,
			CFG.VISUAL.PHYSICAL_BUTTON_NEON_ALPHA)
		ring.CanQuery=false -- Whole button always clicks its handle.
	end
	local outline=box(structure,"ENGRAVED_HARDWARE_NAMEPLATE",
		position+Vector3.new(0,-0.07,1.83),
		Vector3.new(7.0,0.09,1.25),C.black,Enum.Material.Metal)
	local title=caption(outline,Enum.NormalId.Top,legend,46,C.ivory,
		Vector2.new(340,90))
	title.TextScaled=false;title.TextWrapped=false
	title.Font=Enum.Font.GothamBold
	title.TextStrokeTransparency=0.75
	local feedback=ball(structure,"TINY_STATUS_PILOT_LED",
		position+Vector3.new(2.68,0.31,-0.89),
		0.25,color,Enum.Material.Neon,0.35)
	local feedbackLight=lamp(feedback,color,0.08,5)
	local detector=Instance.new("ClickDetector")
	detector.MaxActivationDistance=9
	detector.Parent=handle
	local c={name=name,type=kind,root=structure,handle=handle,
		rod=rod,tip=tip,base=base,collar=collar,
		neon=neon,rim=rim,
		status=feedback,statusLight=feedbackLight,
		click=detector,pos=position,color=color,
		lastUsed=-100,pressedUntil=0,angle=0}
	workingControls[name]=c
	return c
end
-- The V1 freestanding 56x18 desk blocked the CAMERA and its seven
-- oversized Neon stations became the subject of the screenshot. The
-- user's reference places a low, compact bank BELOW the left instrument
-- wall; the middle of the floor stays empty for the hydraulic console.
box(interfaces,"LEFT_CONSOLE_RECESSED_STEEL_FOOT",
	Vector3.new(-42.5,26.05,109.5),Vector3.new(35,0.65,13.4),
	C.trim,Enum.Material.Metal,0,true)
for _,x in ipairs({-57,-44,-28}) do
	for _,z in ipairs({104.5,114.2}) do
		box(interfaces,"CNC_OPEN_BENCH_STEEL_SUPPORT",
			Vector3.new(x,26.25,z),Vector3.new(1.1,3.45,1.1),
			C.silver,Enum.Material.Metal,0,true)
	end
end
-- Chest-height controls are physical. The earlier noncolliding tabletop
-- let a full-sized player walk THROUGH the gap between console pedestals.
-- A low FRONT kickplate and solid worktop keep the station accessible.
box(interfaces,"UNDER_DESK_FRONT_ACCESS_KICKPLATE",
	Vector3.new(-42.5,26.6,116.3),Vector3.new(35.2,2.6,0.65),
	C.trim,Enum.Material.Metal,0,true)
part(interfaces,"LOW_ANGLED_INSTRUMENT_SHELF",
	CFrame.new(-42.5,28.3,109.5)
		*CFrame.Angles(math.rad(-4),0,0),
	Vector3.new(35.3,0.61,13.4),C.charcoal,
	Enum.Material.Metal,0,true)
for n=0,18 do
	local x=-57.6+n*1.66
	local led=box(interfaces,"SMALL_DESK_FEEDBACK_ONLY",
		Vector3.new(x,28.97,102.7),
		Vector3.new(0.51,0.11,0.42),
		n%5==0 and C.amber or C.ruby,
		Enum.Material.Neon,0.67)
	led:SetAttribute("Index",n)
end
local coolantControl=makeControl("COOLANT","dial",
	Vector3.new(-55,29.5,107),C.azure,"COOLANT")
local powerControl=makeControl("REACTOR_POWER","lever",
	Vector3.new(-44,29.5,107),C.mint,"POWER")
local laserControl=makeControl("HEATING_LASERS","lever",
	Vector3.new(-33,29.5,107),C.magenta,"LASERS")
local eCoolControl=makeControl("EMERGENCY_COOLANT","lever",
	Vector3.new(-55,29.5,112.5),C.cyan,"E-COOLANT")
local ignitionControl=makeControl("INITIAL_STARTUP","button",
	Vector3.new(-44,29.5,112.5),C.amber,"IGNITION")
local requestControl=makeControl("SHUTDOWN_REQUEST","button",
	Vector3.new(-33,29.5,112.5),C.red,"SHUTDOWN")
-- Independently mounted guarded SCRAM is one small, honest lever.
local scramControl=makeControl("GUARDED_SCRAM","lever",
	Vector3.new(43,29.5,146),C.red,"SCRAM")
local scramCover=box(interfaces,"MANUAL_RELEASE_SAFETY_GLASS",
	scramControl.pos+Vector3.new(0,2.1,-0.88),
	Vector3.new(4.3,5.0,3.3),C.ivory,
	Enum.Material.SmoothPlastic,0.91)
scramCover.CanQuery=false
local scramCoverHome=scramCover.CFrame

-- Raised shutdown console is an actual machine rising from the black floor
-- pit. Its screen/slots are gameplay, not decorative dead buttons.
local consoleParts={}
local consoleModel=folder(interfaces,"RAISING_SHUTDOWN_CONSOLE")
local function consolePart(name,pos,size,color,mat,alpha,collide)
	local p=box(consoleModel,name,pos,size,color,mat,alpha,collide)
	consoleParts[#consoleParts+1]={part=p,home=p.CFrame}
	return p
end
consolePart("UNDERFLOOR_HYDRAULIC_RAM",
	Vector3.new(0,24.5,126),Vector3.new(24,1.5,16),
	C.trim,Enum.Material.DiamondPlate,0,true)
consolePart("CHAMFERED_INDUSTRIAL_PODIUM",
	Vector3.new(0,27.1,126),Vector3.new(30,4,15),
	C.silver,Enum.Material.Metal,0,true)
consolePart("DARK_SLOPING_TACTILE_TOP",
	Vector3.new(0,29.35,126),Vector3.new(29.4,0.58,14.6),
	C.charcoal,Enum.Material.Metal)
local shutdownScreen=consolePart("REAL_WORKING_SHUTDOWN_STATUS",
	Vector3.new(0,31.0,119.65),Vector3.new(24,2.25,0.42),
	C.black,Enum.Material.SmoothPlastic)
local shutdownLabel=caption(shutdownScreen,Enum.NormalId.Back,
	"CARD ACCESS  0/3   /   SHUTDOWN LOCKED",43,C.amber,
	Vector2.new(1080,230))
local cardSlots={}
for i=1,3 do
	local x=-9+(i-1)*9
	local plate=consolePart("PHYSICAL_CARD_SOCKET_"..i,
		Vector3.new(x,29.78,126),Vector3.new(6.2,0.43,4.4),
		C.black,Enum.Material.Metal)
	local slot=consolePart("CARD_SOCKET_CLICKABLE_CONTACT_"..i,
		Vector3.new(x,30.06,126),Vector3.new(4.8,0.24,2.8),
		C.red,Enum.Material.Neon)
	local shell=consolePart("CARD_GOLD_SOCKET_EDGE_"..i,
		Vector3.new(x,29.97,126),Vector3.new(5.4,0.07,3.4),
		C.silver,Enum.Material.Metal)
	local click=Instance.new("ClickDetector")
	click.MaxActivationDistance=8
	click.Parent=slot
	cardSlots[i]={plate=plate,slot=slot,edge=shell,
		click=click,inserted=false}
end
local shutdownButton=consolePart("HEAVY_FINAL_SHUTDOWN_PLUNGER",
	Vector3.new(0,30.01,131.2),Vector3.new(6.7,0.9,2.6),
	C.red,Enum.Material.Neon)
local shutdownButtonClick=Instance.new("ClickDetector")
shutdownButtonClick.MaxActivationDistance=9
shutdownButtonClick.Parent=shutdownButton
local shutdownButtonPlate=consolePart("FINAL_SHUTDOWN_NAMEPLATE",
	Vector3.new(0,29.8,133.5),Vector3.new(11,0.17,1.6),
	C.black,Enum.Material.Metal)
caption(shutdownButtonPlate,Enum.NormalId.Top,
	"ARMED SHUTDOWN",46,C.white,Vector2.new(700,150))
-- A light in the black lift aperture makes the movement physically obvious.
local liftSpines={}
for _,x in ipairs({-18,-9,0,9,18}) do
	liftSpines[#liftSpines+1]=tube(interfaces,
		"HYDRAULIC_LIFT_PISTON",
		Vector3.new(x,15.5,127),Vector3.new(x,23.8,127),
		0.63,C.silver,Enum.Material.Metal)
end
for _,data in ipairs(consoleParts) do
	data.part.CFrame=data.home*CFrame.new(0,-16.5,0)
	data.part.CanCollide=false
end

-- Spatial audio sources at the camera and at the real machinery.
local coreAudio=ball(soundAnchors,"AUDIO_CORE",CORE,
	0.38,C.black,Enum.Material.SmoothPlastic,1)
local roomAudio=box(soundAnchors,"AUDIO_ROOM_SIREN",
	Vector3.new(0,76,155),Vector3.new(2.4,1,1),
	C.charcoal,Enum.Material.Metal)
local hallAudio=box(soundAnchors,"AUDIO_AUTH_HALL",
	Vector3.new(-85,49,144),Vector3.new(2,1,1),
	C.charcoal,Enum.Material.Metal)
local idleHum=soundtrack(CFG.AUDIO.idle,coreAudio,
	"IDLE_CORE_AIR",0.14,true,300)
local turbineHum=soundtrack(CFG.AUDIO.turbine,coreAudio,
	"PUMP_MOTOR_BED",0.12,true,300)
local siren=soundtrack(CFG.AUDIO.siren,roomAudio,
	"ROOM_AIRRAID_SIREN",0.29,true,280)
local siren2=soundtrack(CFG.AUDIO.siren2,roomAudio,
	"SECOND_ALARM_CADENCE",0.22,true,280)
local coolantAudio=soundtrack(CFG.AUDIO.rain,coreAudio,
	"EMERGENCY_SPRINKLERS",0.16,true,260)
if idleHum then idleHum:Play() end
if turbineHum then turbineHum:Play() end

-- ================================================================
-- 6. REACTOR STATE, REAL CONTROLS, CARD AUTHORIZATION, SHUTDOWN LIFT.
-- ================================================================
local COOLANT_STEPS={0,25,50,75,100}
local POWER_STEPS={0,25,50,75,100}
state={
	mode="COLD",temp=26,pressure=18,integrity=100,
	powerIndex=1,power=0,coolIndex=3,cooling=50,
	lasers=false,rods=0,emergency=false,
	emergencyReserve=100,damagedPipes=0,
	warningAt=0,heatHold=0,freezeHold=0,
	startupAt=0,scramAt=0,freezedownAt=0,
	meltdownAt=0,meltdownEvents={},afterAt=0,
	windowBroken=false,
	consoleRaised=false,bunkerSealed=false,
	cardFound={false,false,false},
	cardInserted={false,false,false},
	failedShutdown=false,lateRodJam=false,
	nextCenterBeat=0,beatNumber=0,
	viewEventFlash=0,round=0,
}
local keyColors={C.azure,C.amber,C.magenta}
local liftTimer=0
local roomBeam=beam(damage,"EDGE_EMERGENCY_BLUE_ARC",
	Vector3.new(-53,24.5,105),Vector3.new(-53,78.3,105),
	0.55,C.azure,Enum.Material.Neon,1)
local roomBeamHalo=beam(damage,"EDGE_EMERGENCY_ARC_HALO",
	Vector3.new(-53,24.5,105),Vector3.new(-53,78.3,105),
	1.8,C.cyan,Enum.Material.Neon,1)
local beamFoot=cylY(damage,"EMERGENCY_COLUMN_FLOOR_AURA",
	Vector3.new(-53,24.3,105),1.7,0.12,
	C.azure,Enum.Material.Neon,1)
local beamAnchor=ball(damage,"INDOOR_BEAM_INVISIBLE_LIGHT",
	Vector3.new(-53,53,105),0.25,
	C.black,Enum.Material.SmoothPlastic,1)
local roomBeamLight=lamp(beamAnchor,C.azure,0,28)
local glassScarFolder=folder(fractures,"WINDOW_CRACKS_THAT_STAY")
local ringScarFolder=folder(fractures,"REAL_RING_AND_EMITTER_DAMAGE")
local emergencySteam={}
for _,p in ipairs({
	Vector3.new(-43,31,98),Vector3.new(43,31,98),
	Vector3.new(-45,39,-20),Vector3.new(45,39,-20),
	}) do
	local anchor=ball(damage,"PHYSICAL_STEAM_OUTLET",p,0.42,
		C.trim,Enum.Material.Metal,0.12)
	local fog=particles(anchor,"LOW_CONTRAST_COOLANT_VAPOR",
		SMOKE,7,C.ivory,1.1,5.4,7)
	fog.LightEmission=0.015
	fog.Lifetime=NumberRange.new(0.65,1.45)
	fog.Transparency=NumberSequence.new({
		NumberSequenceKeypoint.new(0,0.72),
		NumberSequenceKeypoint.new(1,1)})
	fog.Acceleration=Vector3.new(0,4,0)
	emergencySteam[#emergencySteam+1]=fog
end
local sparkShowers={}
for n=1,8 do
	local x=(n-4.5)*11.5
	local pos=Vector3.new(x,87,-30)
	local a=ball(damage,"UNLATCHABLE_CEILING_ISOLATOR",
		pos,0.7,C.azure,Enum.Material.Neon,0.83)
	local sparks=particles(a,"CEILING_REAL_SPARK_RAIN",
		SPARK,35,C.orange,0.7,0.1,21)
	sparks.Acceleration=Vector3.new(0,-21,0)
	sparkShowers[#sparkShowers+1]={body=a,emitter=sparks,
		z=pos.Z,index=n}
end

local function actualCoolant()
	local flow=state.cooling
	if state.emergency and state.emergencyReserve>0 then
		flow=math.max(flow,100)
	end
	return flow*math.max(0.11,1-state.damagedPipes*0.087)
end
local function validOperator(player,position)
	local ch=player.Character
	local human=ch and ch:FindFirstChildOfClass("Humanoid")
	local root=ch and ch:FindFirstChild("HumanoidRootPart")
	return root and human and human.Health>0
		and (root.Position-position).Magnitude<CFG.INTERACTION_DISTANCE
end
local function setPilot(control,tint,on)
	control.status.Color=on and tint or C.slate
	control.statusLight.Color=tint
	control.statusLight.Brightness=on and 0.16 or 0.012
	control.neon.Color=tint
	control.neon.Transparency=on and 0.63 or 0.88
end
local function moveLever(control,angle,instant)
	local base=control.pos+Vector3.new(0,0.39,-0.88)
	local top=base+Vector3.new(0,
		math.cos(angle)*1.85,-math.sin(angle)*1.85)
	if not control.rod then return end
	local cf=CFrame.lookAt((base+top)/2,top)
	local tipPos=top+Vector3.new(0,0.43,0)
	if instant then
		control.rod.CFrame=cf
		control.rod.Size=Vector3.new(0.32,0.32,(top-base).Magnitude)
		control.handle.Position=top
		if control.tip then control.tip.Position=tipPos end
	else
		tween(control.rod,0.43,{CFrame=cf,
			Size=Vector3.new(0.32,0.32,(top-base).Magnitude)})
		tween(control.handle,0.43,{Position=top})
		if control.tip then
			tween(control.tip,0.43,{Position=tipPos})
		end
	end
	control.angle=angle
end
local function drawCoolantDial(instant)
	local control=coolantControl
	local phi=math.rad(-115+(state.coolIndex-1)*57.5)
	local base=control.pos+Vector3.new(0,0.68,-0.88)
	local endPoint=base+Vector3.new(math.sin(phi)*1.05,
		0,-math.cos(phi)*1.05)
	local cf=CFrame.lookAt((base+endPoint)/2,endPoint)
	if instant then
		control.rod.CFrame=cf
		control.rod.Size=Vector3.new(0.11,0.11,(endPoint-base).Magnitude)
	else
		tween(control.rod,0.34,{CFrame=cf,
			Size=Vector3.new(0.11,0.11,(endPoint-base).Magnitude)})
	end
	setPilot(control,state.cooling<25 and C.red or C.azure,
		state.cooling>=25)
end
local function drawControls(instant)
	drawCoolantDial(instant)
	moveLever(powerControl,math.rad(-38+(state.powerIndex-1)*19),instant)
	moveLever(laserControl,math.rad(state.lasers and 35 or -34),instant)
	moveLever(eCoolControl,math.rad(state.emergency and 39 or -35),instant)
	moveLever(scramControl,math.rad(state.rods>60 and 42 or -42),instant)
	setPilot(powerControl,C.mint,state.power>=25)
	setPilot(laserControl,C.magenta,state.lasers)
	setPilot(eCoolControl,C.cyan,state.emergency)
	setPilot(scramControl,state.lateRodJam and C.orange or C.red,
		state.rods>55 or state.lateRodJam)
end
local function pressControl(control)
	if control.type~="button" then return end
	local orig=control.handle.CFrame
	tween(control.handle,0.14,{CFrame=orig*CFrame.new(0,-0.105,0),
		Color=C.ivory})
	task.delay(0.2,function()
		if control.handle.Parent then
			tween(control.handle,0.23,{CFrame=orig,Color=control.color})
		end
	end)
end
local function setSideDoor(d,open)
	if d.open==open then return end
	d.open=open
	d.leaf.CanCollide=false -- Never crush a player while translating.
	local shift=CFrame.new(0,open and 20 or 0,0)
	tween(d.leaf,open and 1.0 or 1.4,
		{CFrame=d.home*shift})
	tween(d.strip,open and 1.0 or 1.4,
		{CFrame=d.stripHome*shift,
			Color=open and C.azure or C.mint})
	if not open then
		task.delay(1.55,function()
			if not d.open and d.leaf.Parent then
				d.leaf.CanCollide=true
			end
		end)
	end
	sfx("gate",hallAudio,0.28,open and 1.18 or 0.84,6)
end
local function setBunkerSealed(value,instant)
	if state.bunkerSealed==value and not instant then return end
	state.bunkerSealed=value
	bunkerLamp.Color=value and C.red or C.mint
	local target=value and bunkerGateClosed or bunkerGateOpen
	bunkerGate.CanCollide=false
	if instant then
		bunkerGate.CFrame=target
	else
		tween(bunkerGate,value and 4.6 or 3.2,
			{CFrame=target},Enum.EasingStyle.Sine)
		sfx("gate",roomAudio,0.54,0.72,13)
		shake(0.55,2.5)
	end
	if value then
		task.delay(instant and 0 or 4.8,function()
			if state.bunkerSealed then bunkerGate.CanCollide=true end
		end)
	end
end
local function raiseShutdownConsole(instant)
	if state.consoleRaised then return end
	state.consoleRaised=true
	liftTimer=now()
	for _,data in ipairs(consoleParts) do
		if instant then data.part.CFrame=data.home
		else tween(data.part,3.8,{CFrame=data.home},
			Enum.EasingStyle.Sine) end
	end
	task.delay(instant and 0 or 3.8,function()
		if state.consoleRaised and consoleParts[1].part.Parent then
			consoleParts[1].part.CanCollide=true
			consoleParts[2].part.CanCollide=true
		end
	end)
	if not instant then
		sfx("gate",roomAudio,0.77,0.79,13)
		shake(0.38,2.7)
		flash(0.11,"ice")
	end
end
local function lowerShutdownConsole(instant)
	if not state.consoleRaised and not instant then return end
	state.consoleRaised=false
	for _,data in ipairs(consoleParts) do
		data.part.CanCollide=false
		local hidden=data.home*CFrame.new(0,-16.5,0)
		if instant then data.part.CFrame=hidden
		else tween(data.part,3.4,{CFrame=hidden}) end
	end
	if not instant then sfx("gate",roomAudio,0.35,0.86,8) end
end
local function randomizeAuthorizationCards()
	local sites={}
	for i=1,#cardBays do sites[i]=i end
	for i=#sites,2,-1 do
		local j=rng:NextInteger(1,i)
		sites[i],sites[j]=sites[j],sites[i]
	end
	for _,bay in ipairs(cardBays) do
		bay.slot=nil;bay.used=false
		bay.card.Transparency=1
		bay.card.CanQuery=false
		bay.face.Transparency=1
		bay.face.CanQuery=false
		if bay.tag then bay.tag.Visible=false end
		bay.edge.Transparency=0.7
		bay.edge.Color=C.azure
	end
	state.cardFound={false,false,false}
	state.cardInserted={false,false,false}
	for slot=1,3 do
		local bay=cardBays[sites[slot]]
		bay.slot=slot
		bay.card.Color=keyColors[slot]
		bay.card.Transparency=0.07
		bay.card.CanQuery=true
		bay.face.Transparency=0.1
		bay.face.Color=C.black
		bay.edge.Color=keyColors[slot]
		bay.edge.Transparency=0.17
		if not bay.tag then
			bay.tag=caption(bay.face,Enum.NormalId.Top,
				"AUTH "..slot,41,C.white,Vector2.new(510,175))
		end
		bay.tag.Visible=true
		bay.tag.Text="AUTH 0"..slot
	end
end
local function cardCount()
	local found=0;local inserted=0
	for i=1,3 do
		if state.cardFound[i] then found=found+1 end
		if state.cardInserted[i] then inserted=inserted+1 end
	end
	return found,inserted
end
local modeCaptions={
	COLD="CORE OFFLINE  /  STANDBY",
	STARTUP="INITIALIZING MAIN REACTOR",
	FAILED_STARTUP="IGNITION FAILED  /  GRID RESET",
	ONLINE="CORE SYSTEMS NOMINAL",
	WARNING="CORE HEAT RISING",
	MELTDOWN="CONTAINMENT FAILURE",
	FREEZEDOWN="COOLANT FREEZEDOWN",
	SCRAM="EMERGENCY RODS INSERTED",
	SUCCESS_SHUTDOWN="CONTROLLED SHUTDOWN",
	AFTERMATH="CONTAINMENT LOST",
	RESETTING="AUTOMATED MAINTENANCE",
}
local function updatePhysicalDisplays(current)
	local found,inserted=cardCount()
	local hot=state.mode=="WARNING" or state.mode=="MELTDOWN"
		or state.mode=="AFTERMATH"
	local title=modeCaptions[state.mode] or "CORE CONTROL"
	if state.mode=="STARTUP" then
		local age=math.max(0,current-state.startupAt)
		title=age<.8 and "START COMMAND ACCEPTED"
			or age<13 and "SIX PHYSICAL HEADS DEPLOYING"
			or (world:GetAttribute("ReactorPilotStabilized") or 0)>.01
			and "MAGNETIC FUSION  /  STABILIZING"
			or (world:GetAttribute("ReactorPilotWhiteVolume") or 0)>.995
			and "MAGNETIC WHITE FUSION"
			or (world:GetAttribute("ReactorPilotCyanVolume") or 0)>.995
			and "SIX REAL NOZZLES  /  CYAN FUSION"
			or (world:GetAttribute("ReactorPilotRelayMask") or 0)>0
			and "SIX PHYSICAL LASERS FIRING"
			or (world:GetAttribute("ReactorPilotDarkness") or 0)>.995
			and "CHAMBER POWERDOWN  /  SIX HEADS LIT"
			or "PURGING SIX REAL FUEL NOZZLES"
	end
	if state.failedShutdown and state.mode=="MELTDOWN" then
		title="SHUTDOWN FAILURE / REACTOR CRITICAL"
	end
	mainSign.label.Text=title
	mainSign.label.TextColor3=hot and C.red
		or state.mode=="SUCCESS_SHUTDOWN" and C.cyan
		or state.mode=="FREEZEDOWN" and C.cyan or C.ivory
	if state.mode=="STARTUP" then
		coreReadout.label.Text=string.format("PHYSICAL HEADS %d/6  /  %04.0fC",
			world:GetAttribute("ReactorPilotHeadsAtTip") or 0,state.temp)
	else
		coreReadout.label.Text=string.format(
			"CORE %04.0fC  /  PRESS %03.0f",state.temp,state.pressure)
	end
	leftReadout.label.Text=string.format(
		"FLOW %03d%%  /  E-COOL %03.0f%%",
		state.cooling,state.emergencyReserve)
	rightReadout.label.Text=state.lateRodJam
		and "SCRAM JAMMED"
		or state.rods>75 and "RODS INSERTED"
		or state.mode=="COLD" and "FEEDS OFF / RODS SAFE"
		or state.lasers and "FEEDS ON / HEAT ON"
		or "FEEDS ON / HEAT OFF"
	local failureAge=state.mode=="MELTDOWN"
		and current-state.meltdownAt or 0
	local outOfTime=state.mode=="MELTDOWN" and
		failureAge>CFG.SHUTDOWN_RESCUE_UNTIL
	shutdownLabel.Text=state.consoleRaised and string.format(
		"AUTH %d/3   INSERTED %d/3    %s",
		found,inserted,outOfTime and "TOO LATE"
			or inserted<3 and "LOCKED"
			or state.mode=="COLD" and "AWAIT IGNITION"
			or state.mode=="FAILED_STARTUP" and "RESETTING"
			or "READY")
		or "PODIUM STOWED / AUTHORIZATION REQUIRED"
	shutdownLabel.TextColor3=outOfTime and C.red
		or inserted==3 and state.mode~="COLD"
		and state.mode~="FAILED_STARTUP" and C.mint
		or C.amber
	for i,data in ipairs(cardSlots) do
		data.slot.Color=state.cardInserted[i] and C.mint
			or state.cardFound[i] and C.amber or C.red
	end
	local leftScreen=wallScreenLabels[-1]
	local rightScreen=wallScreenLabels[1]
	if leftScreen then
		leftScreen.Text=string.format(
			"CORE %s\nTEMP %04.0fC\nPWR  %03d%%\nFLOW %03.0f%%",
			state.mode,state.temp,state.power,actualCoolant())
		leftScreen.TextColor3=hot and C.ivory or C.cyan
	end
	if rightScreen then
		local remaining=math.max(0,math.ceil(
			CFG.MELTDOWN_SECONDS-failureAge))
		local live=0
		for _,e in ipairs(emitters) do
			if not e.broken then live=live+1 end
		end
		rightScreen.Text=string.format(
			"CHAMBER\nPRESS %03.0f\nSHELL %03.0f%%\nEMIT %d/6 %s",
			state.pressure,state.integrity,live,
			state.mode=="MELTDOWN" and
				string.format("T-%d:%02d",math.floor(remaining/60),
					remaining%60) or "READY")
		rightScreen.TextColor3=hot and C.orange or C.azure
	end
	-- Left front wall is not a decorative dead UI: all its readouts
	-- reflect the same server state as the real hardware below it.
	if state.mode=="STARTUP" then
		leftFrontTelemetry.label.Text=string.format(
			"HEADS %d/6\nPWR %03d%%\nTEMP %04.0fC",
			world:GetAttribute("ReactorPilotHeadsAtTip") or 0,
			state.power,state.temp)
	else
		leftFrontTelemetry.label.Text=string.format(
			"CORE %s\nPWR %03d%%\nTEMP %04.0fC",
			state.mode,state.power,state.temp)
	end
	leftFrontTelemetry.label.TextColor3=hot and C.ivory or C.warm
	leftFrontCoolant.label.Text=string.format(
		"FLOW %03.0f%%\nE-COOL %03.0f%%\nKEYS %d/3",
		actualCoolant(),state.emergencyReserve,found)
	leftFrontCoolant.label.TextColor3=state.mode=="FREEZEDOWN"
		and C.azure or hot and C.warm or C.ivory
end
for _,bay in ipairs(cardBays) do
	bay.click.MouseClick:Connect(function(player)
		if not bay.slot or bay.used then return end
		if not validOperator(player,bay.card.Position) then return end
		local slot=bay.slot
		bay.used=true
		state.cardFound[slot]=true
		bay.card.Transparency=1;bay.card.CanQuery=false
		bay.face.Transparency=1
		if bay.tag then bay.tag.Visible=false end
		bay.edge.Color=C.mint
		bay.edge.Transparency=0.3
		sfx("panel",hallAudio,0.58,1.02+slot*0.11,5)
		flash(0.1,"ice")
		if not state.consoleRaised then raiseShutdownConsole(false) end
		updatePhysicalDisplays(now())
	end)
end
for i,data in ipairs(cardSlots) do
	data.click.MouseClick:Connect(function(player)
		if not state.consoleRaised or not state.cardFound[i]
			or state.cardInserted[i] then return end
		if not validOperator(player,data.slot.Position) then return end
		state.cardInserted[i]=true
		data.slot.Color=C.mint
		sfx("switch",roomAudio,0.58,1.08+i*0.08,5)
		flash(0.08,"ice")
		updatePhysicalDisplays(now())
	end)
end
-- ================================================================
-- 7. DAMAGE IS MECHANICAL AND ALWAYS CENTERED ON THE VIEWABLE STAR.
-- ================================================================
local function startLeak(id)
	local p=coolantLines[id]
	if not p or p.leaking or p.broken then return end
	p.leaking=true
	if Workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY") then
		-- This old R5 pipe was retired with the Part reactor. State is still
		-- authoritative; actual approved-mesh service pipes are a later asset.
		sfx("hiss",coreAudio,0.4,0.89,12)
		return
	end
	if p.mouth then
		p.mouth.Transparency=0.26
		p.steam.Enabled=true
		p.spray.Enabled=true
		p.spray:Emit(65)
	end
	sfx("hiss",p.pipe,0.4,0.89,12)
end
local function breakLine(id,quiet)
	local p=coolantLines[id]
	if not p or p.broken then return end
	p.broken=true
	state.damagedPipes=state.damagedPipes+1
	p.pipe.Transparency=1
	p.pipe.CanCollide=false
	if Workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY") then
		-- Do NOT spray from the coordinates of an off-world Part pipe.
		if id==3 or id==6 then
			local feed=viewportFeeds[id==3 and 1 or 2]
			if feed.scar then feed.scar.Transparency=1 end
			if feed.jet then feed.jet.Enabled=false end
			if feed.vapor then feed.vapor.Enabled=false end
		end
		if not quiet then
			sfx("rupture",coreAudio,0.55,0.8,15)
			shake(0.36,1.2)
		end
		return
	end
	if p.mouth then
		p.mouth.Transparency=0.07
		p.mouth.Color=C.white
		p.spray.Enabled=true;p.steam.Enabled=true
		p.spray.Rate=114;p.steam.Rate=48
		p.spray:Emit(145)
	end
	if id==3 or id==6 then
		local feed=viewportFeeds[id==3 and 1 or 2]
		feed.pipe.Color=C.burgundy
		if feed.scar then
			feed.scar.Transparency=0.16
			feed.jet.Enabled=true;feed.jet:Emit(110)
			feed.vapor.Enabled=true;feed.vapor:Emit(35)
			fracture(feed.scar.Position,
				feed.scar.Position+Vector3.new(
					-feed.scar.Position.X*0.16/WORLD_SCALE,8,3),8,C.cyan)
		end
	end
	for i=1,3 do
		throwShard(p.pipe,C.trim,rng:NextNumber(0.19,0.33),
			Vector3.new(rng:NextNumber(-26,26),
				rng:NextNumber(5,30),rng:NextNumber(3,25)),14)
	end
	if not quiet then
		sfx("pressure",p.pipe,0.58,0.93,14)
		sfx("rupture",p.pipe,0.55,0.8,15)
		shake(0.36,1.2)
	end
end
local function failEmitter(id,quiet)
	local e=emitters[id]
	if not e or e.broken then return end
	e.broken=true
	if Workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY") then
		-- Keep R5's true fail flag for the six-mask publisher. Its old
		-- spherical scorch, nozzle, and sparks no longer match the GLB positions.
		e.ray.Transparency=1;e.filament.Transparency=1
		e.hotOptic.Enabled=false;e.softOptic.Enabled=false
		if not quiet then
			sfx("steel",coreAudio,0.78,0.76,14)
			sfx("electricity",coreAudio,0.74,0.9,12)
			flash(0.18,"purple");shake(0.88,2.5)
			centerPulse(4.2,0.8,C.magenta)
		end
		return
	end
	e.ray.Transparency=1
	e.filament.Transparency=1
	e.hotOptic.Enabled=false;e.softOptic.Enabled=false
	e.glow.Color=C.red
	e.glow.Transparency=0.94
	e.light.Brightness=0
	e.lens.Transparency=1
	if e.scorch then e.scorch.Transparency=0.13;e.scorch.Color=C.orange end
	if e.sparks then e.sparks.Enabled=true;e.sparks:Emit(165) end
	local old=e.nozzle.CFrame
	tween(e.nozzle,2.7,{CFrame=old*CFrame.new(
		rng:NextNumber(-3,3),rng:NextNumber(-2,2),6)
			*CFrame.Angles(0,math.rad(43),math.rad(38)),
		Color=C.orange},Enum.EasingStyle.Back)
	for i,iris in ipairs(e.iris) do
		if i%3~=0 then
			throwShard(iris,i%2==0 and C.orange or C.silver,
				1.0,Vector3.new(e.axis.X*21+rng:NextNumber(-8,8),
					e.axis.Y*25+rng:NextNumber(3,23),
					rng:NextNumber(14,40)),18)
			iris.Transparency=1
		else
			iris.Color=C.orange
		end
	end
	local spot=e.nozzle and e.nozzle.Position or CORE
	fracture(spot,CORE+Vector3.new(0,0,19),13,
		quiet and C.orange or C.magenta)
	if not quiet then
		sfx("steel",coreAudio,0.78,0.76,14)
		sfx("electricity",coreAudio,0.74,0.9,12)
		flash(0.22,"purple")
		shake(0.88,2.5)
		centerPulse(4.2,0.8,C.magenta)
	end
end
local function tearBand(id,startIndex,count,quiet)
	local band=frontBands[id]
	if not band then return end
	if Workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY") then
		-- Old Part band is off-world: never spawn loose pieces of it in-room.
		for n=0,count-1 do
			band.parts[((startIndex+n-1)%#band.parts)+1].broken=true
		end
		if not quiet then
			sfx("steel",coreAudio,0.49,0.86,9)
			centerPulse(3.1,0.68,C.violet)
		end
		return
	end
	for n=0,count-1 do
		local seg=band.parts[((startIndex+n-1)%#band.parts)+1]
		if not seg.broken then
			seg.broken=true
			if n%2==0 then
				throwShard(seg.part,n%3==0 and C.orange
					or seg.color,1.0,
					Vector3.new(rng:NextNumber(-28,28),
						rng:NextNumber(-10,45),
						rng:NextNumber(7,33)),17)
			end
			seg.part.Transparency=1
		end
	end
	if not quiet then
		sfx("steel",coreAudio,0.49,0.86,9)
		centerPulse(3.1,0.68,C.violet)
	end
end
local function crackPanes(intensity)
	if state.windowBroken then return end
	-- FAZ4.1: duz Part yama catlaklar (HAIRLINE/SPIDER beam parcalari)
	-- kaldirildi. Kademeli gercek 3B cam hasari Faz 4.4 (M14) ile gelecek;
	-- olay sesi/sarsintisi zamanlama isareti olarak korunuyor.
	local _faz41=intensity
	sfx("glass",roomAudio,0.39,0.84,7)
	shake(0.26,0.7)
end
local function shatterWindow()
	if state.windowBroken then return end
	state.windowBroken=true
	for _,pane in ipairs(glassPanes) do
		pane.Transparency=1
		pane.CanCollide=false
		for i=1,12 do
			local shard=part(transient,"HUMANOID_SIZED_GLAZING_SHARD",
				pane.CFrame*CFrame.new(rng:NextNumber(-13,13),
					rng:NextNumber(-15,15),0),
				Vector3.new(rng:NextNumber(0.8,3.4),
					rng:NextNumber(1.0,4.1),0.13),
				C.cyan,Enum.Material.SmoothPlastic,0.19,true)
			shard.Anchored=false
			shard.AssemblyLinearVelocity=Vector3.new(
				rng:NextNumber(-23,23),rng:NextNumber(3,27),
				rng:NextNumber(23,49))
			shard.AssemblyAngularVelocity=Vector3.new(
				rng:NextNumber(-7,7),rng:NextNumber(-7,7),
				rng:NextNumber(-7,7))
			Debris:AddItem(shard,14)
		end
	end
	glassScarFolder:ClearAllChildren()
	-- FAZ4.1: cercevede takili sahte cam yamalari kaldirildi (M14 gelecek).
	sfx("glass",roomAudio,0.95,0.72,15)
	shake(1.1,3.5)
	flash(0.36,"white")
end
local function activateRoomBeam()
	roomBeam.Transparency=0.76
	roomBeamHalo.Transparency=0.94
	beamFoot.Transparency=0.74
	roomBeamLight.Brightness=0.42
	fracture(Vector3.new(-53,74,105),
		Vector3.new(-53,24,105),16,C.cyan)
	sfx("electricity",roomAudio,0.63,1.25,12)
	flash(0.24,"ice")
	shake(0.74,3.8)
end
local function overpressure()
	for _,e in ipairs(emergencySteam) do
		-- Cracked pipe: one brief burst. Permanent 124/s white steam
		-- obscured V1's window for the REST of the meltdown.
		e:Emit(19)
	end
	sfx("coolant",coreAudio,0.76,0.91,15)
	shake(0.52,2.4)
end
local function continuedCorePulse(age)
	state.beatNumber=state.beatNumber+1
	local danger=math.clamp(age/CFG.MELTDOWN_SECONDS,0,1)
	centerPulse(2.4+danger*3.1,0.82+danger*0.5,
		age>275 and C.magenta or C.white)
	if state.beatNumber%3==0 then
		outwardFrontWave(8,45+danger*53,2.1+danger*0.8,
			age>270 and C.red or C.violet)
	end
	sfx("plasma",coreAudio,0.21+danger*0.24,
		rng:NextNumber(0.8,1.13),10)
	if age>135 then shake(0.14+danger*0.32,0.7) end
end
local function flagAt(age,timeStamp,key,action)
	if age>=timeStamp and not state.meltdownEvents[key] then
		state.meltdownEvents[key]=true
		action()
	end
end
local function beginMeltdown(reason)
	if state.mode=="MELTDOWN" or state.mode=="AFTERMATH"
		or state.mode=="RESETTING" then return end
	state.mode="MELTDOWN"
	state.meltdownAt=now()
	state.meltdownEvents={}
	state.beatNumber=0
	state.nextCenterBeat=now()+9
	state.warningAt=now()
	state.failedShutdown=false
	state.viewEventFlash=now()+2
	if siren then siren:Play() end
	if idleHum then tween(idleHum,2,{Volume=0.08,
		PlaybackSpeed=0.72}) end
	if turbineHum then tween(turbineHum,3,{Volume=0.23,
		PlaybackSpeed=1.2}) end
	sfx("quake",coreAudio,0.42,1.07,14)
	centerPulse(4,1.2,C.white)
	outwardFrontWave(10,49,2.4,C.violet)
	shake(0.65,2.7);flash(0.22,"purple")
	local broadcastAt=Workspace:GetServerTimeNow()
	remote:FireAllClients("MUSIC","START",0,
		CFG.AUDIO.opening,broadcastAt,broadcastAt)
	updatePhysicalDisplays(now())
end
local function failedShutdown()
	if state.failedShutdown then return end
	state.failedShutdown=true
	state.lateRodJam=true
	state.rods=38
	scramControl.status.Color=C.orange
	sfx("steel",coreAudio,0.92,0.58,20)
	sfx("electricity",coreAudio,0.83,0.81,12)
	failEmitter(1,false)
	tearBand(2,25,11,false)
	centerPulse(6,1.5,C.white)
	outwardFrontWave(10,96,3.5,C.red)
	shake(1.6,5)
	flash(0.38,"red")
	updatePhysicalDisplays(now())
end
-- A successful shutdown is a real change of state. Temperature and star
-- fall smoothly, rotating field stops, rods descend and sirens go quiet.
local function succeedShutdown()
	if state.mode=="SUCCESS_SHUTDOWN"
		or state.mode=="AFTERMATH" then return end
	state.mode="SUCCESS_SHUTDOWN"
	state.scramAt=now()
	state.rods=100
	state.powerIndex=1;state.power=0
	state.coolIndex=5;state.cooling=100
	state.lasers=false
	state.emergency=false
	if siren then siren:Stop() end
	if siren2 then siren2:Stop() end
	if coolantAudio then coolantAudio:Stop() end
	remote:FireAllClients("MUSIC","STOP")
	drawControls(false)
	centerPulse(2.4,1.2,C.azure)
	outwardFrontWave(8,58,2.6,C.azure)
	sfx("gate",roomAudio,0.63,1.1,13)
	sfx("coolant",coreAudio,0.45,0.88,11)
	shake(0.55,2.1)
	flash(0.23,"ice")
	updatePhysicalDisplays(now())
end
-- The event list is intentionally a developer-only timeline. NO client
-- countdown narrates it; all beats move real geometry/lights/particles.
local function tickMeltdown(dt,current)
	local age=current-state.meltdownAt
	if age>=CFG.MELTDOWN_SECONDS then
		-- detonate() is defined below and supplied through a declaration.
		return "DETONATE"
	end
	if state.emergency then
		state.emergencyReserve=math.max(0,
			state.emergencyReserve-2.5*dt)
		if state.emergencyReserve<=0 then
			state.emergency=false
			if coolantAudio then coolantAudio:Stop() end
			for _,vent in ipairs(emergencySteam) do vent.Enabled=false end
			drawControls(false)
		end
	end
	local coolant=actualCoolant()
	state.temp=math.min(2970,state.temp+
		math.max(3.5,5.1+age*0.013+
			(state.lasers and 2.2 or 0)+state.power*0.014
			-coolant*0.022-(state.emergency and 1.8 or 0))*dt)
	state.pressure=math.min(221,state.pressure+
		(0.21+age*0.006+state.damagedPipes*0.025)*dt)
	state.integrity=math.max(0,state.integrity-
		(0.086+age*0.0009)*dt)
	if current>=state.nextCenterBeat then
		state.nextCenterBeat=current+rng:NextNumber(8.7,13.2)
		continuedCorePulse(age)
	end
	flagAt(age,12,"FIRST_IMBALANCE",function()
		state.viewEventFlash=now()+0.8
		sfx("plasma",coreAudio,0.28,0.95,10)
		outwardFrontWave(9,47,1.7,C.cyan)
	end)
	flagAt(age,36,"EARLY_PANEL_ALARMS",function()
		startLeak(2)
		sfx("pressure",coreAudio,0.28,0.96,11)
		centerPulse(3.1,1.1,C.violet)
	end)
	flagAt(age,63,"MAGNETIC_STRESS",function()
		tearBand(1,8,7,false)
		fracture(CORE+Vector3.new(0,9,26),
			CORE+Vector3.new(-28,22,28),12,C.magenta)
		shake(0.46,1.5)
	end)
	flagAt(age,87,"THE_FIRST_TUBE_CRACKS",function()
		breakLine(3)
		overpressure()
		centerPulse(3.8,1.0,C.white)
	end)
	flagAt(age,110,"RED_ROOM_COMES_ALIVE",function()
		state.viewEventFlash=now()+2.9
		if siren2 then siren2:Play() end
		sfx("siren",roomAudio,0.54,1.05,15)
		shake(0.52,2.6)
		flash(0.23,"red")
	end)
	flagAt(age,143,"FIRST_GIANT_EMITTER_HEAD_RIPS",function()
		failEmitter(2,false)
		tearBand(1,22,8,false)
		crackPanes(0.55)
	end)
	flagAt(age,169,"SCORE_AND_DISTORTION_SHIFT",function()
		remote:FireAllClients("MUSIC","CROSSFADE",0,
			CFG.AUDIO.escalation,Workspace:GetServerTimeNow(),
			Workspace:GetServerTimeNow()-age)
		centerPulse(4.8,1.3,C.white)
		state.viewEventFlash=now()+3
	end)
	flagAt(age,186,"RIGHT_HAND_EMITTER_FALTERS",function()
		failEmitter(3,false)
		breakLine(6)
		tearBand(2,12,9,false)
		shake(1.0,3.2)
	end)
	flagAt(age,207,"VIOLET_FRONT_FIELD_TURNS",function()
		outwardFrontWave(11,73,2.4,C.magenta)
		centerPulse(5.4,1.15,C.violet)
		for i=1,3 do sparkShowers[i].emitter.Enabled=true end
	end)
	flagAt(age,230,"LOWER_CONDUIT_FAILS",function()
		failEmitter(4,false)
		crackPanes(1.05)
		breakLine(8)
		sfx("steel",coreAudio,0.62,0.7,13)
	end)
	flagAt(age,250,"BLUE_SPRINKLER_PRESSURE",function()
		overpressure()
		state.viewEventFlash=now()+2
		tearBand(3,6,12,false)
		sfx("pressure",roomAudio,0.37,0.85,15)
	end)
	flagAt(age,271,"BOTTOM_DIAGONAL_ISOLATOR_BURNS",function()
		failEmitter(5,false)
		tearBand(2,36,10,false)
		centerPulse(5.0,1.4,C.white)
		shake(1.28,4.3)
	end)
	flagAt(age,294,"BRIEF_ALL_WHITE_PRESSURE_OUT",function()
		centerPulse(8.2,1.5,C.white)
		outwardFrontWave(11,91,3.0,C.white)
		flash(0.61,"white")
		sfx("quake",coreAudio,0.72,0.92,25)
	end)
	flagAt(age,305,"FINAL_SCORE_AND_ROOM_FIELD",function()
		remote:FireAllClients("MUSIC","CROSSFADE",0,
			CFG.AUDIO.finale,Workspace:GetServerTimeNow(),
			Workspace:GetServerTimeNow()-age)
		activateRoomBeam()
		state.viewEventFlash=now()+4.5
	end)
	flagAt(age,327,"CONTROL_ROOM_BLUE_LIGHTNING",function()
		fracture(Vector3.new(-20,77,108),
			Vector3.new(-5,28,111),16,C.azure)
		tearBand(1,37,10,false)
		crackPanes(1.4)
		sfx("electricity",roomAudio,0.8,1.12,10)
	end)
	flagAt(age,345,"BOTH_SIDE_HOUSINGS_PUNCH_OUT",function()
		failEmitter(6,false)
		breakLine(1)
		for i=4,8 do sparkShowers[i].emitter.Enabled=true end
		state.viewEventFlash=now()+2.7
	end)
	flagAt(age,363,"CENTRAL_JET_FANS_OUT",function()
		outwardFrontWave(10,103,3.0,C.magenta)
		centerPulse(8,1.5,C.white)
		tearBand(3,25,15,false)
		shake(1.3,4.4)
	end)
	flagAt(age,385,"FRACTURE_WALL_OF_LIGHT",function()
		crackPanes(1.9)
		centerPulse(8.6,1.9,C.magenta)
		outwardFrontWave(14,109,3.3,C.red)
		sfx("quake",coreAudio,0.72,0.83,28)
	end)
	flagAt(age,410,"BUNKER_PREPARES_TO_SEAL",function()
		bunkerLamp.Color=C.amber
		sfx("siren2",roomAudio,0.69,0.85,17)
		shake(0.86,5.3)
	end)
	flagAt(age,424,"LAST_BUNKER_GATE_CLOSE",function()
		setBunkerSealed(true,false)
		breakLine(10,true)
		state.viewEventFlash=now()+10
		flash(0.39,"red")
	end)
	flagAt(age,430,"CORE_CONTRACTS_FOR_ITS_FINAL_BREAK",function()
		centerPulse(4.2,2.2,C.white)
		sfx("pressure",coreAudio,0.87,0.58,20)
		shake(1.4,4.4)
	end)
	-- M14: final laser reaches the observation glass one second before detonation.
	-- shatterWindow() is idempotent, so detonate's fallback remains safe.
	flagAt(age,434,"FINAL_GLASS_LASER_BREAK",function()
		shatterWindow()
	end)
	return nil
end
-- ================================================================
-- 8. AUTHENTIC OUTCOMES: EXPLOSION, COOLANT FREEZE, STARTUP AND RECOVERY.
-- ================================================================
local function detonate(current)
	if state.mode~="MELTDOWN" then return end
	state.mode="AFTERMATH"
	state.afterAt=current
	state.integrity=0
	state.temp=3060
	state.pressure=235
	state.power=0
	state.lasers=false
	state.emergency=false
	state.viewEventFlash=now()+5
	for i=1,6 do
		if not emitters[i].broken then failEmitter(i,true) end
	end
	for _,band in ipairs(frontBands) do
		for i,seg in ipairs(band.parts) do
			if not seg.broken then
				seg.broken=true
				if i%3==0 then
					throwShard(seg.part,i%2==0 and C.orange
						or C.trim,0.88,
						Vector3.new(rng:NextNumber(-46,46),
							rng:NextNumber(-18,66),
							rng:NextNumber(14,71)),16)
				end
				seg.part.Transparency=1
			end
		end
	end
	shatterWindow()
	for _,line in ipairs(coolantLines) do
		if line.spray then line.spray.Enabled=false end
		if line.steam then line.steam.Enabled=true end
	end
	fallingAsh.Enabled=true;fallingAsh:Emit(240)
	coreDust:Emit(500);coreDust.Enabled=false
	for _,smoke in ipairs(chamberMist) do
		smoke:Emit(65)
		smoke.Rate=1
	end
	for _,feed in ipairs(viewportFeeds) do
		if feed.jet and feed.jet.Enabled then feed.jet:Emit(120) end
	end
	roomBeam.Transparency=1
	roomBeamHalo.Transparency=1
	roomBeamLight.Brightness=0
	centerPulse(17,4.1,C.white)
	outwardFrontWave(9,145,5.0,C.white)
	outwardFrontWave(10,132,5.5,C.red)
	sfx("explosion",coreAudio,1,0.87,22)
	sfx("quake",coreAudio,0.81,0.67,32)
	sfx("impact",roomAudio,0.87,0.8,16)
	flash(1,"white")
	shake(3.1,10)
	if siren then siren:Stop() end
	if siren2 then siren2:Stop() end
	if coolantAudio then coolantAudio:Stop() end
	if turbineHum then turbineHum:Stop() end
	remote:FireAllClients("MUSIC","STOP")
	for _,player in ipairs(Players:GetPlayers()) do
		local ch=player.Character
		local human=ch and ch:FindFirstChildOfClass("Humanoid")
		local root=ch and ch:FindFirstChild("HumanoidRootPart")
		if human and root and human.Health>0 then
			local p=root.Position
			local safe=state.bunkerSealed and p.Z>=170
				and p.Z<232 and math.abs(p.X)<23
				and p.Y>22 and p.Y<52
			if not safe then
				local planar=UNITS.new(p.X,0,p.Z)
				local direction=planar.Magnitude>0.1 and planar.Unit
					or Vector3.new(0,0,1)
				root.AssemblyLinearVelocity=
					direction*(57*WORLD_SCALE)+Vector3.new(0,39,0)
				human:TakeDamage(130)
			end
		end
	end
	updatePhysicalDisplays(now())
end
local function setFreezedown()
	if state.mode~="ONLINE" and state.mode~="WARNING" then return end
	state.mode="FREEZEDOWN"
	state.freezedownAt=now()
	state.warningAt=now()
	coreRoot.Color=C.azure
	paleHalo.Color=C.cyan
	for _,fog in ipairs(emergencySteam) do
		fog.Color=ColorSequence.new(C.cyan,C.white)
		fog.Enabled=true
		fog:Emit(66)
	end
	centerPulse(2.5,1.8,C.cyan)
	sfx("coolant",roomAudio,0.51,0.6,15)
	shake(0.51,2.9)
	flash(0.33,"ice")
	updatePhysicalDisplays(now())
end
local function failStartup()
 if state.mode~="STARTUP" then return end
 state.mode="FAILED_STARTUP"
 state.scramAt=now()
 state.rods=100
 state.powerIndex=1;state.power=0
 state.lasers=false
 state.emergency=false
 if coolantAudio then coolantAudio:Stop() end
 for _,vent in ipairs(emergencySteam) do vent.Enabled=false end
 coreLamp.Brightness=0
 drawControls(false)
 updatePhysicalDisplays(now())
end
local function startReactor()
 if state.mode~="COLD" then return end
 if state.power<25 or actualCoolant()<18 then
  pressControl(ignitionControl)
  ignitionControl.status.Color=C.red
  updatePhysicalDisplays(now())
  mainSign.label.Text=state.power<25 and "RAISE POWER LEVER >= 25% TO IGNITE" or "INCREASE COOLANT FLOW TO IGNITE"
  mainSign.label.TextColor3=C.amber
  return
 end
 state.mode="STARTUP"
 state.startupAt=now()
 state.rods=0
 state.integrity=100
 state.temp=26
 state.pressure=18
 -- Physical button response is immediate; no artificial 47-second wait.
 pressControl(ignitionControl)
 updatePhysicalDisplays(now())
end
local function resetMachine()
	state.round=state.round+1
	state.mode="COLD"
	state.temp=26;state.pressure=18;state.integrity=100
	state.powerIndex=1;state.power=0
	state.coolIndex=3;state.cooling=50
	state.lasers=false;state.rods=0
	state.emergency=false;state.emergencyReserve=100
	state.damagedPipes=0;state.heatHold=0;state.freezeHold=0
	state.startupAt=0
	state.scramAt=0;state.freezedownAt=0
	state.meltdownAt=0;state.meltdownEvents={};state.afterAt=0
	state.windowBroken=false;state.failedShutdown=false
	state.lateRodJam=false;state.viewEventFlash=0
	state.nextCenterBeat=0;state.beatNumber=0
	state.bunkerSealed=false
	lowerShutdownConsole(true)
	setBunkerSealed(false,true)
	for _,d in ipairs(sideDoors) do
		d.open=false;d.lastNear=0
		d.leaf.CFrame=d.home;d.strip.CFrame=d.stripHome
		d.leaf.CanCollide=true;d.strip.Color=C.mint
	end
	for _,e in ipairs(emitters) do
		e.broken=false
		e.nozzle.CFrame=e.nozzleHome
		e.nozzle.Color=C.silver
		e.lens.Transparency=0.29
		e.lens.Color=C.azure
		e.light.Color=C.azure
		e.light.Brightness=1.15
		if e.scorch then e.scorch.Transparency=1 end
		if e.sparks then e.sparks.Enabled=false;e.sparks.Rate=105 end
		e.glow.Color=C.violet;e.glow.Transparency=1
		e.ray.Color=C.magenta;e.ray.Transparency=1
		e.filament.Color=C.white;e.filament.Transparency=1
		e.hotOptic.Enabled=false;e.softOptic.Enabled=false
		for _,piece in ipairs(e.body) do
			piece.Color=e.originalBody[piece]
		end
		for _,iris in ipairs(e.iris) do
			iris.Transparency=0
			iris.Color=C.white
		end
	end
	for _,band in ipairs(frontBands) do
		for _,seg in ipairs(band.parts) do
			seg.broken=false
			seg.part.Transparency=seg.alpha
			seg.part.Color=seg.color
		end
	end
	for _,feed in ipairs(viewportFeeds) do
		feed.pipe.Color=C.silver
		if feed.scar then feed.scar.Transparency=1 end
		if feed.jet then feed.jet.Enabled=false end
		if feed.vapor then feed.vapor.Enabled=false end
	end
	for _,line in ipairs(coolantLines) do
		line.broken=false;line.leaking=false
		local hid=line.pipe:GetAttribute("Faz3Hidden")==true
		line.pipe.Transparency=hid and 1 or 0
		line.pipe.CanCollide=not hid
		if line.mouth then
			line.mouth.Transparency=1
			line.mouth.Color=C.cyan
		end
		if line.spray then line.spray.Enabled=false;line.spray.Rate=75 end
		if line.steam then line.steam.Enabled=false;line.steam.Rate=33 end
	end
	for _,pane in ipairs(glassPanes) do
		pane.Transparency=0.98
		pane.CanCollide=true
	end
	glassScarFolder:ClearAllChildren()
	ringScarFolder:ClearAllChildren()
	transient:ClearAllChildren()
	for _,spark in ipairs(sparkShowers) do
		spark.emitter.Enabled=false
		spark.body.Color=C.azure
	end
	for _,fog in ipairs(emergencySteam) do
		fog.Enabled=false
		fog.Color=ColorSequence.new(C.white,C.white)
	end
	coreRoot.Color=C.violet
	coreRoot.Transparency=0.96
	whiteStar.Transparency=1
	corona.Transparency=1
	whiteStar.Color=C.white
	pinkCrown.Color=C.magenta
	paleHalo.Color=C.violet
	coreDust.Enabled=false
	coreSmoke.Enabled=true
	fallingAsh.Enabled=false
	for _,smoke in ipairs(chamberMist) do smoke.Rate=3 end
	for _,spoke in ipairs(coreSpokes) do spoke.Transparency=1 end
	roomBeam.Transparency=1
	roomBeamHalo.Transparency=1
	beamFoot.Transparency=1
	roomBeamLight.Brightness=0
	drawControls(true)
	scramCover.CFrame=scramCoverHome
	scramCover.Transparency=0.91
	bloom.Intensity=CFG.VISUAL.BLOOM_IDLE
	bloom.Threshold=CFG.VISUAL.BLOOM_THRESHOLD
	grade.TintColor=Color3.fromRGB(251,228,229)
	grade.Saturation=-0.06;grade.Contrast=0.045
	atmosphere.Density=0.012
	Lighting.FogColor=Color3.fromRGB(9,17,37)
	Lighting.FogStart=225;Lighting.FogEnd=530
	Lighting.Brightness=1.5
	Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE
	Lighting.Ambient=Color3.fromRGB(138,137,142)
	if siren then siren:Stop() end
	if siren2 then siren2:Stop() end
	if coolantAudio then coolantAudio:Stop() end
	if idleHum then
		idleHum.Volume=0.14
		idleHum.PlaybackSpeed=1
		if not idleHum.IsPlaying then idleHum:Play() end
	end
	if turbineHum then
		turbineHum.Volume=0.12
		turbineHum.PlaybackSpeed=1
		if not turbineHum.IsPlaying then turbineHum:Play() end
	end
	randomizeAuthorizationCards()
	updatePhysicalDisplays(now())
	remote:FireAllClients("MUSIC","STOP")
	remote:FireAllClients("RESET")
end
local function normalSimulation(dt,current)
	local mode=state.mode
	if state.emergency then
		state.emergencyReserve=math.max(0,
			state.emergencyReserve-2.0*dt)
		if state.emergencyReserve<=0 then
			state.emergency=false
			if coolantAudio then coolantAudio:Stop() end
			for _,vent in ipairs(emergencySteam) do
				vent.Enabled=false
			end
			drawControls(false)
		end
	end
	if mode=="FAILED_STARTUP" then
		state.temp=math.max(130,state.temp-18*dt)
		if current-state.scramAt>18 then
			state.mode="COLD";state.rods=0
			drawControls(false)
			updatePhysicalDisplays(now())
		end
		return
	end
	if mode=="STARTUP" then
		local sAge=math.max(0,current-state.startupAt)
		if sAge>3 and (state.power<25 or actualCoolant()<18) then
			failStartup()
			return
		end
		local cyanVol=math.clamp(world:GetAttribute("ReactorPilotCyanVolume") or 0,0,1)
		local whiteVol=math.clamp(world:GetAttribute("ReactorPilotWhiteVolume") or 0,0,1)
		local stab=math.clamp(world:GetAttribute("ReactorPilotStabilized") or 0,0,1)
		local eqTemp=550+state.power*12+(state.lasers and 650 or 0)-actualCoolant()*4.5
		local targetTemp=26+(eqTemp-26)*(cyanVol*0.35+whiteVol*0.65)
		state.temp=state.temp+(targetTemp-state.temp)*math.min(1,0.45*dt)
		local targetPress=18+math.max(0,state.temp-320)*0.063
		state.pressure=state.pressure+(targetPress-state.pressure)*math.min(1,0.5*dt)
		if stab>.995 and whiteVol>.995
			and world:GetAttribute("ReactorPilotHeadsAtTip")==6
			and (world:GetAttribute("ReactorEmitterReadyMask") or 0)==63 then
			state.mode="ONLINE"
			updatePhysicalDisplays(now())
		end
		return
	end
	if mode=="SCRAM" or mode=="SUCCESS_SHUTDOWN" then
		state.temp=math.max(135,state.temp-18*dt)
		state.pressure=math.max(18,state.pressure-1.8*dt)
		if current-state.scramAt>75 then resetMachine() end
		return
	end
	if mode=="FREEZEDOWN" then
		state.temp=math.max(90,state.temp-0.95*dt+
			(state.power>75 and state.lasers and 13*dt or 0))
		state.pressure=math.max(4,state.pressure-0.17*dt)
		if state.temp>460 then
			state.mode="ONLINE";state.freezeHold=0
			for _,f in ipairs(emergencySteam) do f.Enabled=false end
			updatePhysicalDisplays(now())
		elseif current-state.freezedownAt>135 then
			resetMachine()
		end
		return
	end
	if mode=="COLD" then
		state.temp=math.max(26,state.temp-0.31*dt)
		state.pressure=math.max(15,state.pressure-0.16*dt)
		return
	end
	if mode~="ONLINE" and mode~="WARNING" then return end
	local coolant=actualCoolant()
	local target=550+state.power*12+
		(state.lasers and 650 or 0)-coolant*4.5
	-(state.emergency and 320 or 0)
	state.temp=state.temp+(target-state.temp)*
		math.min(1,0.051*dt)
	local desiredPressure=29+math.max(0,state.temp-500)*0.063+
		state.damagedPipes*5.5
	state.pressure=state.pressure+
		(desiredPressure-state.pressure)*math.min(1,0.12*dt)
	state.pressure=math.clamp(state.pressure,0,215)
	if state.temp>1290 or state.pressure>114 then
		if state.mode~="WARNING" then
			state.mode="WARNING"
			state.warningAt=current
			sfx("panel",roomAudio,0.37,0.77,6)
			centerPulse(3.0,0.7,C.orange)
			updatePhysicalDisplays(now())
		end
	elseif state.mode=="WARNING" and state.temp<1090
		and state.pressure<86 then
		state.mode="ONLINE"
		updatePhysicalDisplays(now())
	end
	if state.temp>1640 or state.pressure>168 then
		state.heatHold=state.heatHold+dt
		if state.heatHold>=8 then beginMeltdown("HEAT_RUNAWAY") end
	else
		state.heatHold=math.max(0,state.heatHold-1.2*dt)
	end
	if state.temp<250 and coolant>65 and state.power<=25 then
		state.freezeHold=state.freezeHold+dt
		if state.freezeHold>13 then setFreezedown() end
	else
		state.freezeHold=math.max(0,state.freezeHold-dt)
	end
end
-- ================================================================
-- 9. EACH SWITCH/KEY MAKES A PERSISTENT, SERVER-AUTHORITATIVE CHANGE.
-- ================================================================
local function accepts(control,player)
	local t=now()
	if t-control.lastUsed<0.55 then return false end
	if not validOperator(player,control.handle.Position) then return false end
	control.lastUsed=t
	return true
end
coolantControl.click.MouseClick:Connect(function(player)
	if not accepts(coolantControl,player) then return end
	if state.mode=="AFTERMATH" or state.mode=="RESETTING" then return end
	state.coolIndex=state.coolIndex%#COOLANT_STEPS+1
	state.cooling=COOLANT_STEPS[state.coolIndex]
	drawCoolantDial(false)
	sfx("switch",roomAudio,0.44,
		0.79+state.cooling*0.004,5)
	for _,line in ipairs(coolantLines) do
		line.fill.Color=state.cooling<25 and C.orange or C.azure
	end
	updatePhysicalDisplays(now())
end)
powerControl.click.MouseClick:Connect(function(player)
	if not accepts(powerControl,player) then return end
	if state.mode=="AFTERMATH" or state.mode=="RESETTING"
		or state.mode=="SUCCESS_SHUTDOWN" then return end
	state.powerIndex=state.powerIndex%#POWER_STEPS+1
	state.power=POWER_STEPS[state.powerIndex]
	moveLever(powerControl,
		math.rad(-38+(state.powerIndex-1)*19),false)
	setPilot(powerControl,C.mint,state.power>=25)
	sfx("switch",roomAudio,0.54,
		0.69+state.power/170,6)
	if state.power>=75 then centerPulse(1.9,0.64,C.white) end
	updatePhysicalDisplays(now())
end)
laserControl.click.MouseClick:Connect(function(player)
	if not accepts(laserControl,player) then return end
	if state.mode=="COLD" or state.mode=="AFTERMATH"
		or state.mode=="RESETTING" or state.mode=="SCRAM"
		or state.mode=="SUCCESS_SHUTDOWN" then
		sfx("panel",roomAudio,0.24,0.56,5)
		return
	end
	state.lasers=not state.lasers
	moveLever(laserControl,
		math.rad(state.lasers and 35 or -34),false)
	setPilot(laserControl,C.magenta,state.lasers)
	sfx("laser",coreAudio,0.64,
		state.lasers and 1.0 or 0.57,11)
	if state.lasers then
		centerPulse(3.2,1.15,C.white)
		fracture(CORE+Vector3.new(0,0,26),
			CORE+Vector3.new(32,18,22),9,C.magenta)
		shake(0.26,0.9)
	end
	updatePhysicalDisplays(now())
end)
eCoolControl.click.MouseClick:Connect(function(player)
	if not accepts(eCoolControl,player) then return end
	if state.mode=="COLD" or state.mode=="AFTERMATH"
		or state.emergencyReserve<=0 then
		sfx("panel",roomAudio,0.25,0.62,5)
		return
	end
	state.emergency=not state.emergency
	moveLever(eCoolControl,
		math.rad(state.emergency and 39 or -35),false)
	setPilot(eCoolControl,C.cyan,state.emergency)
	if state.emergency then
		if coolantAudio then coolantAudio:Play() end
		for _,vent in ipairs(emergencySteam) do
			vent.Enabled=true -- Steady low-flow only while E-COOLANT ON.
		end
		overpressure()
		for _,line in ipairs(coolantLines) do
			line.fill.Color=C.cyan
		end
	else
		if coolantAudio then coolantAudio:Stop() end
		for _,e in ipairs(emergencySteam) do e.Enabled=false end
		sfx("switch",roomAudio,0.41,0.74,5)
	end
	updatePhysicalDisplays(now())
end)
ignitionControl.click.MouseClick:Connect(function(player)
	if not accepts(ignitionControl,player) then return end
	if state.mode=="COLD" then startReactor()
	elseif state.mode=="FREEZEDOWN" then
		state.powerIndex=5;state.power=100;state.lasers=true
		drawControls(false)
		sfx("laser",coreAudio,0.37,0.73,10)
	else
		pressControl(ignitionControl)
		sfx("panel",roomAudio,0.28,0.62,5)
	end
end)
requestControl.click.MouseClick:Connect(function(player)
	if not accepts(requestControl,player) then return end
	if state.mode=="AFTERMATH" or state.mode=="RESETTING" then return end
	pressControl(requestControl)
	if not state.consoleRaised then
		raiseShutdownConsole(false)
	else
		local found,inserted=cardCount()
		if found<3 or inserted<3 then
			sfx("panel",roomAudio,0.49,0.61,6)
			requestControl.status.Color=C.red
			flash(0.1,"red")
		end
	end
	updatePhysicalDisplays(now())
end)
scramControl.click.MouseClick:Connect(function(player)
	if not accepts(scramControl,player) then return end
	if state.mode=="AFTERMATH" or state.mode=="RESETTING"
		or state.mode=="SUCCESS_SHUTDOWN" or state.lateRodJam then return end
	if state.mode=="COLD" then
		sfx("panel",roomAudio,0.3,0.6,4)
		return
	end
	tween(scramCover,0.48,{CFrame=scramCoverHome*CFrame.new(0,4,0),
		Transparency=1})
	sfx("gate",roomAudio,0.54,0.89,9)
	local age=state.mode=="MELTDOWN"
		and now()-state.meltdownAt or 0
	local _,inserted=cardCount()
	if state.mode=="MELTDOWN" and
		(age>CFG.SHUTDOWN_RESCUE_UNTIL or
			(age>100 and inserted<3) or actualCoolant()<18) then
		failedShutdown()
		drawControls(false)
	else
		succeedShutdown()
	end
end)
shutdownButtonClick.MouseClick:Connect(function(player)
	if not state.consoleRaised or not
		validOperator(player,shutdownButton.Position) then return end
	if state.mode=="AFTERMATH" or state.mode=="RESETTING"
		or state.mode=="SUCCESS_SHUTDOWN" then return end
	if state.mode=="COLD" or state.mode=="FAILED_STARTUP" then
		sfx("panel",roomAudio,0.36,0.62,5)
		shutdownButton.Color=C.orange
		task.delay(0.65,function()
			if shutdownButton.Parent then shutdownButton.Color=C.red end
		end)
		return
	end
	local _,inserted=cardCount()
	if inserted<3 then
		shutdownButton.Color=C.red
		sfx("panel",roomAudio,0.47,0.63,6)
		flash(0.12,"red")
		updatePhysicalDisplays(now())
		return
	end
	shutdownButton.Color=C.white
	tween(shutdownButton,0.17,{Size=Vector3.new(6.7,0.55,2.6)})
	task.delay(0.5,function()
		shutdownButton.Size=Vector3.new(6.7,0.9,2.6)
		shutdownButton.Color=C.red
	end)
	local bad=state.mode=="MELTDOWN" and
		now()-state.meltdownAt>CFG.SHUTDOWN_RESCUE_UNTIL
		or state.temp>2590 or state.lateRodJam
		or actualCoolant()<18
	if bad then
		if state.mode~="MELTDOWN" then
			beginMeltdown("BOTCHED_SHUTDOWN")
		end
		failedShutdown()
	else
		succeedShutdown()
	end
end)
-- ================================================================
-- 10. CONTINUOUS VISUAL REACTIVITY; ALL EFFECTS ARE WORLD OBJECTS.
-- ================================================================
local animationTime=0
local visualRods=0
local relayTrace=""
local lastPilotRelayMask=0
local function animate(dt,current)
	animationTime=animationTime+dt
	-- Authoritative state for reviewed GLB mesh assemblies. Only publishes
	-- existing server simulation; never accepts a client-provided mode.
	world:SetAttribute("ReactorMeshSignal",1)
	world:SetAttribute("ReactorMode",state.mode)
	local pilot=state.mode=="STARTUP"
	-- R5 retains lighting authority. The new physical Pilot provides only a
	-- 0..1 chamber-dark request after the approved fuel hold.
	local pilotDark=pilot and math.clamp(
		world:GetAttribute("ReactorPilotDarkness") or 0,0,1) or 0
	local pilotWhite=pilot and math.clamp(
		world:GetAttribute("ReactorPilotWhiteVolume") or 0,0,1) or 0
	local startupAge=pilot and math.max(0,current-state.startupAt) or 0
	world:SetAttribute("ReactorStartupAge",startupAge)
	world:SetAttribute("ReactorPilotAuthorityStamp",Workspace:GetServerTimeNow())
	world:SetAttribute("ReactorStartupPhase",pilot and
		(world:GetAttribute("ReactorPilotStage") or "PILOT_PENDING") or state.mode)
	world:SetAttribute("ReactorGridDrop",false)
	world:SetAttribute("ReactorStartupChamberOutage",0)
	world:SetAttribute("ReactorMeltdownAge",state.mode=="MELTDOWN"
		and math.max(0,current-state.meltdownAt) or 0)
	world:SetAttribute("ReactorPower",state.power)
	world:SetAttribute("ReactorIntegrity",state.integrity)
	-- Four M13 ruptures follow real simulation failures; the order deliberately
	-- maps existing R5 line IDs to upper-left, upper-right, rear-left, rear-right.
	local ruptureMask=0
	for bitIndex,lineId in ipairs({6,3,8,1}) do
		if coolantLines[lineId] and coolantLines[lineId].broken then
			ruptureMask += 2^(bitIndex-1)
		end
	end
	world:SetAttribute("ReactorPipeBrokenMask",ruptureMask)
	-- Each reviewed physical mesh head corresponds 1:1 to an R5 emitter.
	-- Prime relays one at a time; export REAL failure events, not invented
	-- visual timers. No client-controlled action can set these values.
	local readyMask,brokenMask=0,0
	for i,e in ipairs(emitters) do
		local relay=state.mode~="COLD" and state.mode~="FAILED_STARTUP"
			and state.mode~="SCRAM" and state.mode~="SUCCESS_SHUTDOWN"
			and state.mode~="AFTERMATH" and state.mode~="RESETTING"
		if pilot then
			-- 04: only R5 may energize a physical relay. Clock age alone is
			-- insufficient: verify the approved GLB exists, its own nozzle
			-- socket is actually near the center, and its actual piston stroke
			-- reached the tip. No client signal, orphan ray or broken emitter.
			relay=false
			if startupAge>=35.5
				and (pilotDark>.995 or pilotWhite>.01 or startupAge>=38.0)
				and world:GetAttribute("ReactorPilotReady")==true
				and world:GetAttribute("ReactorPilotHeadsAtTip")==6
				and not e.broken then
				local scene=Workspace:FindFirstChild("REACTOR_MESH_ASSEMBLY")
				local moving=scene and scene:FindFirstChild("MOVING")
				local tag=emitterSites[i].tag
				local head=moving and moving:FindFirstChild(
					"REACTOR_EMITTER_REV03_"..tag)
				local tip=head and head:FindFirstChild("NOZZLE__white",true)
				local socket=tip and tip:FindFirstChild(
					"PILOT_FUEL_SOCKET_"..tag)
				relay=scene and
					(scene:GetAttribute("ReactorPilotStroke_"..tag) or 0)>.995
					and tip and tip:IsA("MeshPart") and socket
					and socket:IsA("Attachment")
					and (socket.WorldPosition-
						UNITS.new(0,26.5,2.7)).Magnitude<9
			end
		end
		if relay then readyMask+=2^(i-1) end
		if e.broken then brokenMask+=2^(i-1) end
	end
	if not pilot then
		relayTrace="";lastPilotRelayMask=0
	elseif readyMask~=lastPilotRelayMask then
		lastPilotRelayMask=readyMask
		if readyMask>0 then
			relayTrace=relayTrace..string.format("%d@%.2f|",
				readyMask,startupAge)
		end
	end
	world:SetAttribute("ReactorPilotRelayMask",pilot and readyMask or 0)
	world:SetAttribute("ReactorPilotRelayTrace",relayTrace)
	world:SetAttribute("ReactorEmitterReadyMask",readyMask)
	world:SetAttribute("ReactorEmitterBrokenMask",brokenMask)
	world:SetAttribute("ReactorLaserBoost",state.lasers==true)
	local pipeLeakMask,pipeBrokenMask=0,0
	for i,p in ipairs(coolantLines) do
		if p.leaking then pipeLeakMask+=2^(i-1) end
		if p.broken then pipeBrokenMask+=2^(i-1) end
	end
	world:SetAttribute("ReactorPipeLeakMask",pipeLeakMask)
	world:SetAttribute("ReactorPipeBrokenMask",pipeBrokenMask)
	local melting=state.mode=="MELTDOWN"
	local cold=state.mode=="COLD" or state.mode=="FAILED_STARTUP"
	local age=melting and current-state.meltdownAt or 0
	local progress=melting and math.clamp(age/CFG.MELTDOWN_SECONDS,0,1)
		or 0
	local phase=(math.sin(animationTime*(melting and 5+progress*8
		or 2.8))+1)/2
	local alarm=melting or state.mode=="WARNING"
		or state.mode=="AFTERMATH" or state.failedShutdown
	local redRoom=melting and math.clamp((age-76)/119,0,1)
		or state.mode=="AFTERMATH" and 1
		or state.mode=="WARNING" and 0.22 or 0
	-- Existing meltdown/emergency lighting remains server-owned.
	local blackout=melting and age>115 and
		math.sin(animationTime*(age>305 and 18 or 7))<-0.65
		or current<state.viewEventFlash
		and math.sin(animationTime*31)<-0.39
		-- The old procedural star is entirely OFF in CHECKPOINT 01.
		-- Non-startup damage/freezedown visuals remain with gameplay.
		local dark=cold or pilot
		local size=dark and .30
			or state.mode=="FREEZEDOWN" and .8
			or (state.mode=="SCRAM" or
				state.mode=="SUCCESS_SHUTDOWN") and .68
			or state.mode=="AFTERMATH" and .58
			or melting and 1+progress*.33+phase*(.07+progress*.14)
			or 1+phase*.025+state.power*.0007
		if melting and age>418 then
			local u=math.clamp((age-418)/17,0,1)
			size=u<.7 and 1.43-u*1.28 or .55+((u-.7)/.3)^2*2.1
		end
		local coreTint=state.mode=="FREEZEDOWN" and C.cyan
			or state.mode=="AFTERMATH" and C.orange
			or dark and C.navy
			or melting and age>250 and C.red
			or melting and age>100 and C.magenta or C.violet
		coreRoot.Color=coreTint
		coreRoot.Size=Vector3.new(15.6,15.6,15.6)*size
		coreRoot.Transparency=dark and 1 or .62
		whiteStar.Color=state.mode=="AFTERMATH" and C.orange
			or state.mode=="FREEZEDOWN" and C.cyan or C.white
		whiteStar.Size=Vector3.new(12.6,12.6,12.6)*size
		whiteStar.Transparency=dark and 1 or .015
		corona.Size=Vector3.new(22,22,22)*size
		corona.Transparency=dark and 1 or melting and .82 or .86
		pinkCrown.Color=coreTint
		pinkCrown.Size=Vector3.new(25,25,25)*math.max(.65,size)
		pinkCrown.Transparency=dark and 1 or .82
		paleHalo.Color=melting and age>190 and C.red or C.violet
		paleHalo.Size=Vector3.new(38,38,38)*math.max(.7,size)
		paleHalo.Transparency=dark and 1 or .93
		coreLamp.Color=melting and (age>300 and C.magenta or C.ivory)
			or state.mode=="AFTERMATH" and C.orange
			or state.mode=="FREEZEDOWN" and C.azure
			or Color3.fromRGB(226,238,252)
		coreLamp.Brightness=dark and 0
			or math.min(CFG.VISUAL.CORE_LIGHT_MAX,
			state.mode=="AFTERMATH" and 1.1
			or state.mode=="FREEZEDOWN" and 1.4
			or melting and 2.65+progress*1.95+phase*.62
			or 0.20+state.power*.0015+phase*.04)
		coreDust.Enabled=not dark and state.mode~="AFTERMATH"
			and state.mode~="RESETTING"
		coreDust.Rate=dark and 0 or melting and 42+progress*95
			or state.lasers and 48 or 26
		coreSmoke.Rate=dark and 0 or melting and 31+progress*75
			or state.mode=="FREEZEDOWN" and 24 or 16
		for _,mist in ipairs(chamberMist) do
			mist.Rate=dark and 0 or melting and 9+progress*8 or 7
		end
		for i,cloud in ipairs(remoteNebula) do
			cloud.Color=melting and (i%5==0 and C.magenta
				or i%3==0 and C.violet or C.cobalt)
				or i%9==0 and C.violet or C.nebula
			cloud.Transparency=dark and 1
				or melting and .61+phase*.09 or .73
		end
		for n,spoke in ipairs(coreSpokes) do
			spoke.Transparency=dark and 1
				or n%2==0 and .89 or melting and .12 or .42
		end
		for i,e in ipairs(emitters) do
			local surge=e.broken and melting and
				math.sin(animationTime*10.2+i*2.8)>-.35
			local glitch=melting and age>92 and
				math.sin(animationTime*11+i*2.8)<-.48
			e.ray.Color=surge and C.orange
				or melting and age>250 and C.orange or C.magenta
			e.ray.Transparency=dark and 1
				or e.broken and (surge and .72 or .97)
				or glitch and .89 or state.lasers and .61+phase*.1
				or .77+phase*.06
			e.filament.Transparency=dark and 1
				or e.broken and (surge and .65 or 1)
				or glitch and .79 or melting and .08+phase*.1
				or state.lasers and .13+phase*.09 or .37
			e.hotOptic.Enabled=not dark and not e.broken and not glitch
		e.softOptic.Enabled=not dark and not e.broken
			e.hotOptic.Width0=(melting and 2.6+progress*1.5
				or 2.3)*WORLD_SCALE
			e.glow.Transparency=dark and 1
				or e.broken and (surge and .9 or .98)
				or state.lasers and .92 or .96
			e.glow.Color=melting and age>270 and C.red or C.violet
			e.lens.Color=dark and C.slate
				or melting and age>280 and C.orange
				or state.mode=="FREEZEDOWN" and C.cyan or C.azure
			e.lens.Transparency=dark and 1 or .29
			e.light.Color=e.lens.Color
			e.light.Brightness=dark and 0
				or e.broken and (surge and .44 or 0)
				or glitch and .11 or melting and 1.1+phase*.75
				or state.lasers and .86 or .43
				for _,segment in ipairs(e.body) do
				if segment.Material==Enum.Material.Neon then
					segment.Color=melting and age>270 and C.red
						or melting and age>235 and C.orange
						or state.mode=="FREEZEDOWN" and C.cyan
						or e.originalBody[segment]
					segment.Transparency=dark and 1
						or e.broken and .48+phase*.16 or .42
				end
			end
		end
		if melting and age>305 and roomBeamLight.Brightness>0 then
			roomBeam.Transparency=0.56+phase*0.26
			roomBeamHalo.Transparency=0.9+phase*0.07
			roomBeamLight.Brightness=0.18+phase*0.42
		end
	for _,band in ipairs(frontBands) do
		local velocity=dark and .05
			or melting and 1.2+progress*3.7
			or state.mode=="SUCCESS_SHUTDOWN" and 0.18 or 1
		local cf=CFrame.new(CORE+Vector3.new(0,0,band.depth))
			*CFrame.Angles(0,0,animationTime*band.speed*velocity)
		for _,segment in ipairs(band.parts) do
			if not segment.broken then
				segment.part.CFrame=cf*segment.home
				segment.part.Color=melting and age>210 and
					(segment.color==C.silver and C.orange
						or age>325 and C.red or C.magenta)
					or segment.color
				segment.part.Transparency=dark and 1 or segment.alpha
			end
		end
	end
	for i,arc in ipairs(dynamicArcs) do
		local active=melting and
			i<=(5+math.floor(progress*20))
			and math.sin(animationTime*(8+progress*12)+i*2)>-0.66
			or not melting and not dark and
			state.mode~="AFTERMATH" and state.lasers and i<=5
		if active then
			local a=i*2.39996+animationTime*0.19
			local b=a+math.sin(animationTime*4.1+i)*0.54
			local radius=9+(i%4)*3
			local outer=27+(i%7)*2.0
			local p=CORE+Vector3.new(math.cos(a)*radius,
				math.sin(a)*radius,25)
			local q=CORE+Vector3.new(math.cos(b)*outer,
				math.sin(b)*outer,26)
			arc.CFrame=CFrame.lookAt((p+q)/2,q)
			arc.Size=UNITS.new((i%5==0 and 0.52 or 0.24)*WORLD_SCALE,
				(i%5==0 and 0.52 or 0.24)*WORLD_SCALE,
				(q-p).Magnitude)
			arc.Color=melting and age>305 and C.red
				or i%9==0 and C.white or C.magenta
			arc.Transparency=i%5==0 and 0.49 or 0.59
		else arc.Transparency=1 end
	end
	visualRods=visualRods+(state.rods-visualRods)*
		math.min(1,dt*2.2)
	for _,rod in ipairs(rods) do
		local y=97-visualRods*0.24
		rod.body.Position=Vector3.new(rod.x,y,rod.z)
		rod.tip.Position=Vector3.new(rod.x,y-13,rod.z)
		rod.tip.Color=state.lateRodJam and C.orange
			or visualRods>50 and C.red or C.azure
	end
	for _,line in ipairs(coolantLines) do
		local amount=math.max(0.15,actualCoolant()/100*21)
		line.fill.Size=Vector3.new(amount,11.1,11.1)
		line.fill.CFrame=FRAME.new(line.x,(4+amount/2)*WORLD_SCALE,
			line.z)
			*CFrame.Angles(0,0,math.pi/2)
		line.fill.Color=line.broken and C.orange
			or state.mode=="FREEZEDOWN" and C.cyan
			or state.cooling<25 and C.amber or C.cobalt
	end
	local tick=math.floor(animationTime*(melting and 4.7 or 0.75))
	for _,cell in ipairs(matrixLamps) do
		local urgency=alarm and (cell.col*3+cell.row+tick)%8<
			(melting and age>230 and 6 or melting and 4 or 2)
		local tint=urgency and C.red
			or alarm and cell.row%3==0 and C.orange
			or cell.normal
		cell.part.Color=blackout and C.black or tint
		cell.part.Transparency=blackout and 0.84
			or urgency and tick%2==0 and 0.34 or 0.63
	end
	for _,cell in ipairs(frontIndicatorCells) do
		local urgent=alarm and (cell.row*5+cell.col+tick)%9<4
		cell.part.Color=urgent and C.red or cell.normal
		cell.part.Transparency=blackout and 0.9
			or urgent and 0.36 or 0.62
	end
	for _,dot in ipairs(frontStatusLamps) do
		local pulse=alarm and (dot.group+dot.index+tick)%7<5
		dot.part.Color=pulse and C.red or C.ruby
		dot.part.Transparency=blackout and 0.54
			or pulse and 0.06 or 0.28
	end
	for _,bar in ipairs(waveformBars) do
		local h=0.8+math.abs(math.sin(animationTime*2.2+
			bar.n*0.6+bar.side))*
			(melting and 5.4 or 2.6)
		bar.part.Size=Vector3.new(0.62,h,0.18)
		bar.part.CFrame=bar.home*CFrame.new(0,(h-2.8)*0.16,0)
		bar.part.Color=alarm and
			(redRoom>0.48 and C.red or C.amber) or C.mint
	end
	for _,b in ipairs(ceilingBulbs) do
		local tint=redRoom>.4 and (b.index%4==0 and C.magenta or C.red)
			or alarm and b.index%3==0 and C.amber or b.normal
		b.part.Color=blackout and C.charcoal or tint
		b.part.Transparency=blackout and .9 or .62
		if b.point then
			b.point.Color=tint
			b.point.Brightness=blackout and 0
				or melting and .19+phase*.17 or .13
		end
	end
	bigLampBezel.Color=redRoom>.45 and C.red or C.ruby
	bigLampDiffuser.Color=C.ivory
	bigLampPoint.Color=redRoom>.65 and C.warm or C.ivory
	bigLampPoint.Brightness=blackout and .12
		or redRoom>.5 and .68 or .49
	for _,bar in ipairs(alarmFixtures) do
		local tint=alarm and (redRoom>.29 and C.red or C.warm) or C.ivory
		bar.body.Color=blackout and C.frame or tint
		bar.light.Color=tint
		bar.light.Brightness=blackout and 0
			or alarm and (.55+phase*.39) or .18
	end
	for _,flood in ipairs(floorFloods) do
		local tint=redRoom>.5 and C.red or alarm and C.ruby or C.warm
		flood.body.Color=blackout and C.frame or tint
		flood.point.Color=tint
		flood.point.Brightness=(blackout and 0
			or melting and .61+.24*math.abs(math.sin(
				animationTime*2+flood.index*.37)) or .07)
			*(1-pilotDark)
	end
	for _,light in ipairs(chamberServiceLights) do
		light.Brightness=.68*(1-pilotDark)
	end
	for _,light in ipairs(chamberWashLights) do
		light.Brightness=1.25*(1-pilotDark)
	end
	for _,fill in ipairs(roomFillLights) do
		fill.Color=C.ivory:Lerp(C.red,redRoom*.9)
		fill.Brightness=blackout and .15 or 1.02-redRoom*.47
	end
	bloom.Intensity=melting and CFG.VISUAL.BLOOM_IDLE+
		progress*(CFG.VISUAL.BLOOM_MELTDOWN-CFG.VISUAL.BLOOM_IDLE)
		or state.mode=="AFTERMATH" and .38 or CFG.VISUAL.BLOOM_IDLE
	bloom.Threshold=CFG.VISUAL.BLOOM_THRESHOLD
	if state.mode=="AFTERMATH" then
		local fading=current-state.afterAt<3.5
		Lighting.Brightness=fading and 2.05 or 1.35
		Lighting.ExposureCompensation=fading and -.17 or -.55
		Lighting.Ambient=Color3.fromRGB(125,46,57)
		grade.TintColor=Color3.fromRGB(255,184,177)
		grade.Saturation=-.07
		atmosphere.Density=.047
	elseif state.mode=="FREEZEDOWN" then
		Lighting.Brightness=1.92
		Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE
		Lighting.Ambient=Color3.fromRGB(67,93,133)
		grade.TintColor=Color3.fromRGB(211,228,244)
		grade.Saturation=-.09
		atmosphere.Density=.028
	elseif state.mode=="SUCCESS_SHUTDOWN" then
		Lighting.Brightness=1.95
		Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE
		Lighting.Ambient=Color3.fromRGB(97,110,111)
		grade.TintColor=Color3.fromRGB(232,237,229)
		grade.Saturation=-.04
		atmosphere.Density=.014
	else
		Lighting.Brightness=blackout and .93 or 2.05-redRoom*.49
		Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE-redRoom*.2
		Lighting.Ambient=Color3.fromRGB(138,137,142):Lerp(
			Color3.fromRGB(150,36,47),redRoom*.8)
		grade.TintColor=Color3.fromRGB(252,249,246):Lerp(
			Color3.fromRGB(255,114,128),redRoom*.7)
		grade.Saturation=.015+redRoom*.145
		grade.Contrast=.045+redRoom*.13
		atmosphere.Density=.012+redRoom*.025
		Lighting.FogColor=Color3.fromRGB(9,17,37):Lerp(
			Color3.fromRGB(91,20,37),redRoom)
		Lighting.FogStart=225-redRoom*160
		Lighting.FogEnd=530-redRoom*365
	end
	-- Only the reactor volume powers down in CHECKPOINT 03. Existing
	-- gallery PointLights and 3D instruments remain powered; this is NOT a
	-- full-screen overlay or a client camera/screen-blackening trick.
	if pilotDark>0 then
		Lighting.Brightness=2.05+(0.26-2.05)*pilotDark
		Lighting.ExposureCompensation=CFG.VISUAL.ROOM_EXPOSURE-.68*pilotDark
		Lighting.Ambient=Color3.fromRGB(138,137,142):Lerp(
			Color3.fromRGB(2,4,9),pilotDark)
		Lighting.OutdoorAmbient=Color3.fromRGB(59,58,70):Lerp(
			Color3.fromRGB(2,3,8),pilotDark)
		grade.Brightness=.055*(1-pilotDark)
		grade.Contrast=.045+.10*pilotDark
		grade.Saturation=.015-.09*pilotDark
		atmosphere.Density=.012*(1-pilotDark)
		-- A modest white-photon bloom around the existing effect volume;
		-- never a full-screen overlay or a replacement core object.
		bloom.Intensity=CFG.VISUAL.BLOOM_IDLE*(1-.60*pilotDark)
			+.19*pilotWhite
		bloom.Size=22+16*pilotWhite
		bloom.Threshold=CFG.VISUAL.BLOOM_THRESHOLD-.29*pilotWhite
	else
		local onlineGlow = (state.mode=="ONLINE" or state.mode=="WARNING") and 1 or 0
		bloom.Intensity=CFG.VISUAL.BLOOM_IDLE+.02*onlineGlow
		bloom.Size=22+4*onlineGlow
		bloom.Threshold=CFG.VISUAL.BLOOM_THRESHOLD-.03*onlineGlow
		Lighting.OutdoorAmbient=Color3.fromRGB(59,58,70)
		grade.Brightness=.055
	end
end
-- ================================================================
-- 11. SPAWNING, AUTOMATIC AIRLOCKS, JOIN-IN-PROGRESS, PLAY LOOP.
-- ================================================================
-- A window-level test, not a promise about an unplayed Studio build.
-- Mark sample rays as suspicious if any non-glass WORLD part in the lab
-- blocks the reactor. The audit reports warnings in Studio's Output.
local function auditView()
	-- Geometric rays alone MISS Roblox's Glass material depth-pass bug.
	for _,pane in ipairs(glassPanes) do
		if pane.Material==Enum.Material.Glass then
			warn("[CORE PROTOCOL V3] Glass masks translucent reactor graphics")
		end
	end
	local params=RaycastParams.new()
	params.FilterType=Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances={chamber,machine,damage,
		service,soundAnchors}
	local samples={}
	-- All six MECHANICAL HEADS, not only the center, must be visible from
	-- the ACTUAL diagonal player spawn; V1's audit tested the wrong place.
	for _,cameraHeight in ipairs({31,35}) do
		local referenceEye=Vector3.new(-29,cameraHeight,151)
		for _,e in ipairs(emitters) do
			samples[#samples+1]={
				name=e.tag.."_EYE_"..cameraHeight,
				eye=referenceEye,
				target=CORE+e.axis*(29*WORLD_SCALE)+Vector3.new(0,0,18)}
		end
		samples[#samples+1]={
			name="STAR_EYE_"..cameraHeight,eye=referenceEye,
			target=CORE+Vector3.new(0,0,27)}
	end
	for _,eyeX in ipairs({-6,0,6}) do
		for _,targetX in ipairs({-14,0,14}) do
			samples[#samples+1]={
				name="CENTER_"..eyeX.."_"..targetX,
				eye=Vector3.new(eyeX,35,151),
				target=CORE+Vector3.new(targetX,0,27)}
		end
	end
	local good=0
	for _,sample in ipairs(samples) do
		local p=sample.eye
		local unobstructed=true
		for _=1,11 do
			local direction=sample.target-p
			if direction.Magnitude<0.5 then break end
			local hit=Workspace:Raycast(p,direction,params)
			if not hit then break end
			local piece=hit.Instance
			if (piece:IsDescendantOf(gallery) or
				piece:IsDescendantOf(interfaces))
				and piece.Transparency<0.9 then
				unobstructed=false
				warn("[CORE PROTOCOL V2] Blocked "..sample.name..
					" by "..piece.Name)
				break
			end
			p=hit.Position+direction.Unit*(0.4*WORLD_SCALE)
		end
		if unobstructed then good=good+1 end
	end
	print(string.format(
		"[CORE PROTOCOL REMAKE] Geometry rays: %d/%d clear "..
			"(six heads at TWO camera heights, core + nine samples). "..
			"Brightness/appearance still need Studio screenshot comparison.",
		good,#samples))
end
local function syncPlayer(player)
	if state.mode~="MELTDOWN" then
		remote:FireClient(player,"MUSIC","STOP")
		return
	end
	local age=now()-state.meltdownAt
	local stage,at,id
	if age>=305 then
		stage="CROSSFADE";at=state.meltdownAt+305
		id=CFG.AUDIO.finale
	elseif age>=169 then
		stage="CROSSFADE";at=state.meltdownAt+169
		id=CFG.AUDIO.escalation
	else
		stage="START";at=state.meltdownAt
		id=CFG.AUDIO.opening
	end
	-- UTC server-time synchronization for late arrivals, independent of
	-- local time() epochs, which are deliberately not shared with clients.
	local elapsed=now()-at
	remote:FireClient(player,"MUSIC",stage,elapsed,id,
		Workspace:GetServerTimeNow()-elapsed,
		Workspace:GetServerTimeNow()-age)
end
local syncCooldown={}
remote.OnServerEvent:Connect(function(player,command)
	if command~="SYNC" then return end
	local t=now()
	if syncCooldown[player] and t-syncCooldown[player]<4 then return end
	syncCooldown[player]=t
	syncPlayer(player)
end)
local function prepareCharacter(ch)
	local root=ch:WaitForChild("HumanoidRootPart",12)
	if not root or not ch.Parent then return end
	task.wait(0.1)
	if root.Parent and ch.Parent then
		root.CFrame=CFrame.lookAt(Vector3.new(-29,30.7,151),
			Vector3.new(-40,30.7,18))
		root.AssemblyLinearVelocity=Vector3.zero
	end
end
local function onPlayer(player)
	player.CharacterAdded:Connect(prepareCharacter)
	if player.Character then task.spawn(prepareCharacter,player.Character) end
end
Players.PlayerAdded:Connect(onPlayer)
Players.PlayerRemoving:Connect(function(player)
	syncCooldown[player]=nil
end)
for _,player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end
local function pollAirlocks(current)
	for _,d in ipairs(sideDoors) do
		local nearby=false
		for _,player in ipairs(Players:GetPlayers()) do
			local ch=player.Character
			local root=ch and ch:FindFirstChild("HumanoidRootPart")
			local human=ch and ch:FindFirstChildOfClass("Humanoid")
			if root and human and human.Health>0
				and math.abs(root.Position.X-d.home.Position.X)<12.5
				and math.abs(root.Position.Z-d.home.Position.Z)<12
				and root.Position.Y<51 then
				nearby=true
				break
			end
		end
		if nearby then
			d.lastNear=current
			if not d.open then setSideDoor(d,true) end
		elseif d.open and current-d.lastNear>2.9 then
			setSideDoor(d,false)
		end
	end
end
resetMachine()
auditView()
if RunService:IsStudio() then
	local oldQA=game:GetService("ServerStorage"):FindFirstChild("__STUDIO_QA_SWITCH")
	if oldQA then oldQA:Destroy() end
	local qaFn=Instance.new("BindableFunction")
	qaFn.Name="__STUDIO_QA_SWITCH"
	qaFn.OnInvoke=function(cmd)
		if cmd=="DROP_POWER_ZERO" then
			state.powerIndex=1;state.power=0
			moveLever(powerControl,math.rad(-38),false)
			setPilot(powerControl,C.mint,false)
			updatePhysicalDisplays(now())
			return "POWER_DROPPED_TO_0"
		elseif cmd=="PULL_SCRAM" then
			tween(scramCover,0.48,{CFrame=scramCoverHome*CFrame.new(0,4,0),Transparency=1})
			succeedShutdown()
			return "SCRAM_PULLED_SUCCESS_SHUTDOWN"
		elseif cmd=="TOGGLE_LASER_BOOST" then
			state.lasers=not state.lasers
			moveLever(laserControl,math.rad(state.lasers and 35 or -34),false)
			setPilot(laserControl,C.magenta,state.lasers)
			updatePhysicalDisplays(now())
			return "LASERS_"..tostring(state.lasers)
		elseif cmd=="START_PREVIEW_25" then
			if state.mode~="COLD" then return "ALREADY_"..tostring(state.mode) end
			state.powerIndex=2;state.power=25
			drawControls(false)
			startReactor()
			return "STARTED_PREVIEW_25"
		end
		return "UNKNOWN_CMD"
	end
	qaFn.Parent=game:GetService("ServerStorage")
end
if CFG.STUDIO_AUTO_STARTUP and RunService:IsStudio() then
	task.delay(2,function()
		if state.mode~="COLD" then return end
		state.powerIndex=2;state.power=25
		drawControls(false)
		startReactor()
		print("[CORE PROTOCOL R4] Studio-only automatic STARTUP visual preview; no input events.")
	end)
end
if CFG.STUDIO_AUTO_MELTDOWN and RunService:IsStudio() then
	task.delay(12,function()
		if state.mode~="COLD" then return end
		state.powerIndex=5;state.power=100
		state.coolIndex=2;state.cooling=25
		state.lasers=true
		state.temp=1705;state.pressure=135
		drawControls(false)
		beginMeltdown("STUDIO_CINEMATIC_TEST")
		local preview=math.clamp(tonumber(
			CFG.STUDIO_PREVIEW_SECOND) or 0,0,430)
		if preview>0 then
			-- Developer-only VISUAL fast-forward. Process irreversible
			-- damage once; transient bursts settle in a few seconds.
			-- Real gameplay timing remains unmodified when preview=0.
			state.meltdownAt=now()-preview
			state.temp=math.min(2870,1705+preview*4.2)
			state.pressure=math.min(215,135+preview*0.16)
			state.integrity=math.max(0,
				100-preview*(0.086+preview*0.00045))
			state.nextCenterBeat=now()+10
			tickMeltdown(0,now())
			print("[CORE PROTOCOL V2] Studio visual preview "..
				"at t="..preview.."s; allow 5s for bursts to settle.")
		end
		updatePhysicalDisplays(now())
	end)
end
local tickBudget={animation=0,text=0,door=0}
RunService.Heartbeat:Connect(function(delta)
	local current=now()
	local dt=math.clamp(delta,0,0.24)
	if state.mode=="MELTDOWN" then
		local result=tickMeltdown(dt,current)
		if result=="DETONATE" then detonate(current) end
	elseif state.mode=="AFTERMATH" then
		if current-state.afterAt>=CFG.RESET_DELAY then
			resetMachine()
		end
	else
		normalSimulation(dt,current)
	end
	tickBudget.animation=tickBudget.animation+dt
	tickBudget.text=tickBudget.text+dt
	tickBudget.door=tickBudget.door+dt
	-- 11 Hz synchronized world animation; server gameplay is still
	-- simulated on EVERY heartbeat and remains authoritative.
	if tickBudget.animation>=0.09 then
		animate(tickBudget.animation,current)
		tickBudget.animation=0
	end
	if tickBudget.text>=0.67 then
		updatePhysicalDisplays(current)
		tickBudget.text=0
	end
	if tickBudget.door>=0.23 then
		pollAirlocks(current)
		tickBudget.door=0
	end
end)
print("[CORE] Physical server ready. CHECKPOINT 02: six real mechanical fuel sources; "..
	"no photons or automatic ONLINE. Meltdown gameplay retained.")

