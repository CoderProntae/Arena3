--!nonstrict
-- KONTROL 01-05 SERVER MECHANICAL & STATE PILOT (ZERO 2D PARTICLES / BEAMS)
-- Drives the six real approved GLB emitter heads, telescoping pistons, and
-- sliding wall hatches rigidly, and publishes authoritative synchronized
-- state scalars (Fuel, Darkness, RelayMask, CyanVolume, WhiteVolume) for the
-- 60 FPS Real-Time 3D EditableMesh Volumetric & Fluid Engine.
-- Holds cleanly at Kontrol 05 (WHITE_PLASMA_HOLD_FOR_USER_APPROVAL); never
-- enters ONLINE automatically. Non-startup gameplay remains untouched.
local Workspace = game:GetService("Workspace")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

local assembly = Workspace:WaitForChild("REACTOR_MESH_ASSEMBLY", 60)
local world = Workspace:WaitForChild("CORE_PROTOCOL_V2_WORLD", 60)
if not assembly or not world then
	warn("[PILOT 3D] Missing approved reactor assembly or gameplay world")
	return
end
if assembly:GetAttribute("EmitterModuleCount") ~= 6 then
	warn("[PILOT 3D] Six approved emitters required; refusing startup")
	return
end
local moving = assembly:WaitForChild("MOVING", 10)
if not moving then
	warn("[PILOT 3D] Missing MOVING GLB assembly")
	return
end

local sites = {
	{tag = "UPPER", axis = Vector3.new(0, 1, 0), start = 0.7},
	{tag = "LEFT", axis = Vector3.new(-1, 0, 0), start = 1.65, hatch = 1},
	{tag = "RIGHT", axis = Vector3.new(1, 0, 0), start = 2.2, hatch = -1},
	{tag = "LOWER_LEFT", axis = Vector3.new(-0.72, -0.694, 0).Unit, start = 3.1},
	{tag = "LOWER_RIGHT", axis = Vector3.new(0.72, -0.694, 0).Unit, start = 4.0},
	{tag = "LOWER", axis = Vector3.new(0, -1, 0), start = 4.7},
}

local function model(parent, name)
	local item = parent:FindFirstChild(name)
	assert(item and item:IsA("Model"), "Approved physical GLB missing: " .. name)
	return {item = item, at = item:GetPivot()}
end

local function glide(t)
	t = math.clamp(t, 0, 1)
	return t * t * (3 - 2 * t)
end

local function bit(mask, i)
	return math.floor(mask / 2 ^ (i - 1)) % 2 == 1
end

local rigs = {}
for _, site in ipairs(sites) do
	local head = model(moving, "REACTOR_EMITTER_REV03_" .. site.tag)
	local motor = model(moving, "REACTOR_PISTON_GUIDE_01_" .. site.tag)
	local children = {}
	for _, piece in ipairs({"STAGE1", "STAGE2", "STAGE3", "PUSHER"}) do
		children[piece] = model(motor.item, piece)
	end
	local doors = nil
	if site.hatch then
		local hatch = model(moving, "REACTOR_WALL_HATCH_THROUGH_01_" .. site.tag)
		doors = {a = model(hatch.item, "LEAF_LEFT"), b = model(hatch.item, "LEAF_RIGHT")}
	end
	rigs[#rigs + 1] = {site = site, head = head, stages = children, doors = doors}
end
assert(#rigs == 6)

local totalRate = 0
for _, r in ipairs(rigs) do
	local tip = r.head.item:FindFirstChild("NOZZLE__white", true)
	assert(tip and tip:IsA("MeshPart"), "Approved nozzle tip missing: " .. r.site.tag)
	local oldSocket = tip:FindFirstChild("PILOT_FUEL_SOCKET_" .. r.site.tag)
	if oldSocket then oldSocket:Destroy() end
	local socket = Instance.new("Attachment")
	socket.Name = "PILOT_FUEL_SOCKET_" .. r.site.tag
	local vent = tip.Position - r.site.axis * 0.09
	socket.CFrame = tip.CFrame:ToObjectSpace(CFrame.lookAt(vent, vent - r.site.axis))
	socket.Parent = tip

	local oldLight = tip:FindFirstChild("PILOT_NOZZLE_REFLECTED_VAPOR_LIGHT_" .. r.site.tag)
	if oldLight then oldLight:Destroy() end
	local light = Instance.new("PointLight")
	light.Name = "PILOT_NOZZLE_REFLECTED_VAPOR_LIGHT_" .. r.site.tag
	light.Color = Color3.fromRGB(222, 232, 242)
	light.Range = 8
	light.Brightness = 0
	light.Shadows = false
	light.Enabled = false
	light.Parent = tip

	local optic = r.head.item:FindFirstChild("OPTIC__cyan", true)
	r.optic = (optic and optic:IsA("MeshPart")) and optic or nil
	r.opticBaseColor = r.optic and r.optic.Color or Color3.fromRGB(61, 178, 255)
	r.opticBaseMat = r.optic and r.optic.Material or Enum.Material.Neon
	r.socket = socket
	r.light = light
	r.flowRate = ({
		UPPER = 1.6,
		LEFT = 4.2,
		RIGHT = 4.2,
		LOWER_LEFT = 6.2,
		LOWER_RIGHT = 6.2,
		LOWER = 2.8,
	})[r.site.tag]
	totalRate += r.flowRate
end

local anchor = assembly:WaitForChild("MESH_EFFECTS_INVISIBLE_ANCHOR", 20)
local focus = anchor and anchor:FindFirstChild("CORE_FOCUS")
local fixed = assembly:FindFirstChild("STATIC")
local approvedCore = fixed and fixed:FindFirstChild("REACTOR_CORE_MANYETIK_01")

local orbitRings = {}
local hiddenCoreBalls = {}
if approvedCore then
	for _, m in ipairs(approvedCore:GetDescendants()) do
		if m:IsA("MeshPart") then
			if m.Name:find("^ORBIT_") then
				orbitRings[#orbitRings + 1] = {
					part = m,
					baseColor = m.Color,
					baseMaterial = m.Material,
				}
			elseif m.Name:find("^CENTER__") then
				hiddenCoreBalls[#hiddenCoreBalls + 1] = {
					part = m,
					baseColor = m.Color,
					baseMaterial = m.Material,
				}
			end
		end
	end
end

if focus and focus:IsA("Attachment") then
	local wp = focus.WorldPosition
	focus.WorldCFrame = CFrame.new(wp.X, wp.Y, 2.70)
elseif focus and focus:IsA("BasePart") then
	local wp = focus.Position
	focus.CFrame = CFrame.new(wp.X, wp.Y, 2.70)
end
local coreChamberLight = nil
if focus then
	local prev = focus:FindFirstChild("PILOT_3D_CHAMBER_CORE_LIGHT")
	if prev then prev:Destroy() end
	coreChamberLight = Instance.new("PointLight")
	coreChamberLight.Name = "PILOT_3D_CHAMBER_CORE_LIGHT"
	coreChamberLight.Brightness = 0
	coreChamberLight.Range = 46
	coreChamberLight.Shadows = false
	coreChamberLight.Color = Color3.fromRGB(48, 218, 252)
	coreChamberLight.Parent = focus
end

local function resetAllVisualState()
	for _, r in ipairs(rigs) do
		r.light.Enabled = false
		r.light.Brightness = 0
	end
	if coreChamberLight then
		coreChamberLight.Brightness = 0
	end
	for _, orb in ipairs(orbitRings) do
		orb.part.Transparency = 1
		orb.part.Color = orb.baseColor
		orb.part.Material = orb.baseMaterial
	end
	for _, ball in ipairs(hiddenCoreBalls) do
		ball.part.Transparency = 1
		ball.part.Color = ball.baseColor
		ball.part.Material = ball.baseMaterial
	end
	local atmos = Lighting:FindFirstChild("CORE_PROTOCOL_V2_ATMOS")
	if atmos and atmos:IsA("Atmosphere") then
		atmos.Haze = 0.018
	end
	world:SetAttribute("ReactorPilotDarkness", 0)
	world:SetAttribute("ReactorPilotFuel", 0)
	world:SetAttribute("ReactorPilotFuelNozzles", 0)
	world:SetAttribute("ReactorPilotCustomSmokeRate", 0)
	world:SetAttribute("ReactorPilotPhotonSources", 0)
	world:SetAttribute("ReactorPilotCyanVolume", 0)
	world:SetAttribute("ReactorPilotWhiteVolume", 0)
	world:SetAttribute("ReactorPilotStabilized", 0)
	world:SetAttribute("ReactorPilotCoreMeshActive", 0)
	world:SetAttribute("ReactorPilotParticleBudget", 0)
	world:SetAttribute("ReactorPilotStockSmokeEmitters", 0)
end

local function moveRig(r, age)
	local s = r.site
	local gate = glide((age - s.start) / 1.4)
	local stroke = glide((age - s.start - 1.4) / 6.4)
	local travel = -s.axis * (19.8 * stroke)
	local push = CFrame.new(travel)
	r.stages.STAGE1.item:PivotTo(CFrame.new(-s.axis * (6.6 * stroke)) * r.stages.STAGE1.at)
	r.stages.STAGE2.item:PivotTo(CFrame.new(-s.axis * (13.2 * stroke)) * r.stages.STAGE2.at)
	r.stages.STAGE3.item:PivotTo(push * r.stages.STAGE3.at)
	r.stages.PUSHER.item:PivotTo(push * r.stages.PUSHER.at)
	r.head.item:PivotTo(push * r.head.at)
	if r.doors then
		local slide = s.hatch * 5.85 * gate
		r.doors.a.item:PivotTo(CFrame.new(0, 0, slide) * r.doors.a.at)
		r.doors.b.item:PivotTo(CFrame.new(0, 0, -slide) * r.doors.b.at)
	end
	assembly:SetAttribute("ReactorPilotGate_" .. s.tag, math.clamp((age - s.start) / 1.4, 0, 1))
	assembly:SetAttribute("ReactorPilotStroke_" .. s.tag, math.clamp((age - s.start - 1.4) / 6.4, 0, 1))
	return gate, stroke
end

world:SetAttribute("ReactorPilotReady", true)
world:SetAttribute("ReactorPilotOwner", false)
world:SetAttribute("ReactorPilotStage", "COLD")
world:SetAttribute("ReactorPilotMoving", 0)
world:SetAttribute("ReactorPilotHeadsAtTip", 0)
world:SetAttribute("ReactorPilot3DGeometryMode", "REAL_3D_EDITABLE_MESH_VOLUMETRICS")
world:SetAttribute("ReactorPilotNewVisibleParts", 0)
world:SetAttribute("ReactorPilotStatus", "READY_REAL_3D_NO_2D_EFFECTS")
resetAllVisualState()

local owned = false
local latchedFullRelays = false
local clock = 0
RunService.Heartbeat:Connect(function(dt)
	clock += math.min(dt, 0.2)
	if clock < 0.05 then return end
	clock = 0

	local active = world:GetAttribute("ReactorMode") == "STARTUP"
	if not active then
		latchedFullRelays = false
		if owned then
			resetAllVisualState()
			owned = false
			world:SetAttribute("ReactorPilotOwner", false)
			world:SetAttribute("ReactorPilotMoving", 0)
			world:SetAttribute("ReactorPilotStatus", "RETURNED_TO_GAMEPLAY_CONTROLLER")
		end
		world:SetAttribute("ReactorPilotStage", world:GetAttribute("ReactorMode") or "COLD")
		return
	end
	if not owned then
		owned = true
		world:SetAttribute("ReactorPilotOwner", true)
	end

	local ok, problem = pcall(function()
		local age = world:GetAttribute("ReactorStartupAge") or 0
		local movingCount, atTip = 0, 0
		for _, r in ipairs(rigs) do
			local gate, stroke = moveRig(r, age)
			if (gate > 0.005 and gate < 0.995) or (stroke > 0.005 and stroke < 0.995) then
				movingCount += 1
			end
			if stroke > 0.995 then atTip += 1 end
		end
		world:SetAttribute("ReactorPilotMoving", movingCount)
		world:SetAttribute("ReactorPilotHeadsAtTip", atTip)

		local darkRamp = atTip == 6 and glide((age - 21.0) / 4.0) or 0
		local fuel = atTip == 6 and glide((age - 13.0) / 2.6) * (1 - darkRamp) or 0
		local darkHold = darkRamp > 0.995
		local rawMask = world:GetAttribute("ReactorPilotRelayMask") or 0
		if darkHold and rawMask == 63 then
			latchedFullRelays = true
		end
		local mask = latchedFullRelays and 63 or (darkHold and rawMask or 0)
		local fullRelays = latchedFullRelays or (mask == 63)
		local cyan = fullRelays and glide((age - 37.4) / 2.2) or 0
		local white = fullRelays and glide((age - 48.0) / 5.0) or 0
		local stabilize = (fullRelays and white > 0.995) and glide((age - 55.5) / 6.0) or 0
		local darkness = darkRamp * (1 - stabilize)

		local liveFuel, rateSum, livePhotons = 0, 0, 0
		for i, r in ipairs(rigs) do
			local fAmt = fuel * r.flowRate
			local relayOn = bit(mask, i)
			if fAmt > 0.15 then
				liveFuel += 1
				rateSum += fAmt
			end
			if relayOn then livePhotons += 1 end

			r.light.Enabled = fAmt > 0.15 or darkRamp > 0.002
			local nozzleCol = Color3.fromRGB(224, 234, 244)
				:Lerp(Color3.fromRGB(204, 238, 252), darkRamp * 0.65)
				:Lerp(Color3.fromRGB(226, 242, 255), white * 0.65)
			r.light.Color = nozzleCol
			r.light.Brightness = 0.28 * fuel + darkRamp * (relayOn and 0.55 or 0.38)
			r.light.Range = 7 + darkRamp * 1.5
		end

		-- Keep static center spheres and static un-animated ORBIT meshes hidden so
		-- our living 3-axis-rotating & boiling 3D EditableMesh spheres own the core!
		for _, ball in ipairs(hiddenCoreBalls) do
			ball.part.Transparency = 1
		end
		for _, orb in ipairs(orbitRings) do
			orb.part.Transparency = 1
		end

		if coreChamberLight then
			coreChamberLight.Color = Color3.fromRGB(208, 234, 250):Lerp(Color3.fromRGB(216, 230, 252), white)
			coreChamberLight.Brightness = (cyan * 0.24 * (1 - white) + white * 0.20) * (1 - stabilize)
			coreChamberLight.Range = 22
		end

		local atmos = Lighting:FindFirstChild("CORE_PROTOCOL_V2_ATMOS")
		if atmos and atmos:IsA("Atmosphere") then
			atmos.Density = 0.012 * (1 - darkness) + 0.028 * fuel
			atmos.Haze = 0.018 + 0.22 * fuel
		end

		world:SetAttribute("ReactorPilotFuel", math.floor(fuel * 1000 + 0.5) / 1000)
		world:SetAttribute("ReactorPilotDarkness", math.floor(darkness * 1000 + 0.5) / 1000)
		world:SetAttribute("ReactorPilotFuelNozzles", liveFuel)
		world:SetAttribute("ReactorPilotCustomSmokeRate", math.floor(rateSum + 0.5))
		world:SetAttribute("ReactorPilotPhotonSources", livePhotons)
		world:SetAttribute("ReactorPilotCyanVolume", math.floor(cyan * 1000 + 0.5) / 1000)
		world:SetAttribute("ReactorPilotWhiteVolume", math.floor(white * 1000 + 0.5) / 1000)
		world:SetAttribute("ReactorPilotStabilized", math.floor(stabilize * 1000 + 0.5) / 1000)
		world:SetAttribute("ReactorPilotCoreMeshActive", 0)

		world:SetAttribute("ReactorPilotStage",
			stabilize > 0.995 and "STABILIZED_HANDOFF_TO_ONLINE"
			or stabilize > 0.01 and "MAGNETIC_FUSION_STABILIZING"
			or white > 0.995 and "WHITE_PLASMA_IGNITED"
			or cyan > 0.995 and "CYAN_FUSION_ACTIVE"
			or mask > 0 and "SIX_REAL_PHYSICAL_RELAYS_SEQUENCING"
			or darkHold and "DARK_CHAMBER_READY"
			or liveFuel == 6 and "FUEL_INJECTION_ACTIVE"
			or atTip == 6 and "DARK_CHAMBER_TRANSITION"
			or "SIX_REAL_HEADS_DEPLOYING"
		)
		world:SetAttribute("ReactorPilotStatus",
			stabilize > 0.995 and "CHECKPOINT_06_STABILIZED_READY_FOR_ONLINE"
			or stabilize > 0.01 and "CHECKPOINT_06_STABILIZING_ROOM_AND_STAR"
			or white > 0.995 and "CHECKPOINT_05_REAL_3D_MAGNETIC_STAR"
			or cyan > 0.995 and "CHECKPOINT_04_REAL_3D_CONDUITS_CYAN_CORE"
			or mask > 0 and "CHECKPOINT_04_PHYSICAL_RELAYS_3D"
			or darkHold and "CHECKPOINT_03_SIX_LIT_GLBS_DARK_VOLUME"
			or "CHECKPOINT_02_REAL_3D_PLUMES_AND_CHAMBER_MIST"
		)
	end)

	if not ok then
		resetAllVisualState()
		world:SetAttribute("ReactorPilotOwner", false)
		world:SetAttribute("ReactorPilotReady", false)
		world:SetAttribute("ReactorPilotStatus", "ERROR: " .. tostring(problem):sub(1, 110))
		warn("[PILOT 3D] Mechanical/state loop stopped: " .. tostring(problem))
		script.Disabled = true
	end
end)

print("[PILOT 3D] Six physical GLBs + authoritative 02-05 state ready. Zero 2D ParticleEmitter/Beam.")
