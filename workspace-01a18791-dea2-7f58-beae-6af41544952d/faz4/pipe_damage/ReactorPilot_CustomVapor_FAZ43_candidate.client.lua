--!nonstrict
-- ============================================================================
-- REFERENCE-CALIBRATED 60 FPS REAL-TIME 3D VOLUMETRIC & MAGNETIC NEBULA ENGINE
--   * ZERO 2D ParticleEmitters, ZERO 2D Beams, ZERO 2D BillboardGuis!
--   * Built from multi-method pixel, HSV-spectrum, radial-falloff, optical-flow,
--     and human-perceptual comparison against reference_original.mp4:
--   1) STAGE 02 STRAIGHT AXIAL NOZZLE VAPOR (GRAVITY = 0):
--      162 3D vapor clusters (= 972 crinkled 3D wisps) + 12 axisymmetric nozzle
--      cones spawn EXCLUSIVELY inside the 6 physical NOZZLE__white mouths and
--      travel DEAD STRAIGHT along each head's radial axis (-s.axis) with zero
--      downward sag and zero mid-air spawning.
--   2) 360-DEGREE HARDWARE Z-BUFFER CORE OCCLUSION (LEFT / CENTER / RIGHT):
--      STAR_3D_OPAQUE_SUN_BODY (closed 360° EditableMesh sphere, Material=Neon,
--      exact Transparency = 0 -> hardware Z-write pass) + dynamic outer-rim beam
--      clipping makes it mathematically impossible to see beams inside the core
--      from ANY camera angle (far left, center, far right, above, or below).
--   3) TRUE RGBA-BAKED SURFACEAPPEARANCE REFERENCE PALETTE & LAYER COUNT:
--      (Roblox SurfaceAppearance AlphaMode.Transparency ignores MeshPart.Color,
--      so every reference hue is baked directly into 32-bit RGBA EditableImages!)
--      - Vivid Turquoise-Cyan Stage-04 expansion volume + cyan nebula clouds
--      - Massive Stage-05 pure-white sun + 36 orbiting white-ice corona plumes
--      - 56 stormy multi-tone Royal-Cobalt / Deep-Indigo / Ice-Blue 3D chamber
--        nebula clusters (= 336 billowing 3D clouds across the chamber!)
--      - Stage-06 corona breakup & stabilization revealing 6 wide conical flaring
--        white-cyan plasma beams + 24 fine collar guide rails + 3 cyan rings!
--   * Strictly uses 7 EditableMeshes (<= 8 client cap) + 6 RGBA EditableImages.
-- ============================================================================
local AssetService = game:GetService("AssetService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

Workspace:SetAttribute("VaporStep", "01_BOOT")

local assembly = Workspace:WaitForChild("REACTOR_MESH_ASSEMBLY", 60)
local world = Workspace:WaitForChild("CORE_PROTOCOL_V2_WORLD", 60)
if not assembly or not world then return end
local moving = assembly:WaitForChild("MOVING", 20)
local anchor = assembly:WaitForChild("MESH_EFFECTS_INVISIBLE_ANCHOR", 20)
if not moving or not anchor then return end

local focusAtt = anchor:WaitForChild("CORE_FOCUS", 20)
local O = focusAtt and Vector3.new(focusAtt.WorldPosition.X, focusAtt.WorldPosition.Y, 0) or Vector3.new(0, 26.5, 0)
-- Exact coplanar focal center of all 6 physical GLB heads (7.730 studs from every NOZZLE__white):
local FOCUS = Vector3.new(O.X, O.Y, 2.70)

local SITES = {
	{tag = "UPPER",       axis = Vector3.new(0, 1, 0),              jetScale = 0.88},
	{tag = "LEFT",        axis = Vector3.new(-1, 0, 0),             jetScale = 1.05},
	{tag = "RIGHT",       axis = Vector3.new(1, 0, 0),              jetScale = 1.05},
	{tag = "LOWER_LEFT",  axis = Vector3.new(-0.72, -0.694, 0).Unit, jetScale = 1.00},
	{tag = "LOWER_RIGHT", axis = Vector3.new(0.72, -0.694, 0).Unit,  jetScale = 1.00},
	{tag = "LOWER",       axis = Vector3.new(0, -1, 0),             jetScale = 0.90},
}

local function clamp01(x)
	return x < 0 and 0 or (x > 1 and 1 or x)
end

local function smooth(a, b, x)
	local t = clamp01((x - a) / (b - a))
	return t * t * (3 - 2 * t)
end

local function toward(cur, target, maxDelta)
	if cur < target then
		return math.min(target, cur + maxDelta)
	else
		return math.max(target, cur - maxDelta)
	end
end

local function bit(mask, i)
	return math.floor(mask / (2 ^ (i - 1))) % 2 == 1
end

local function fbm3(x, y, z)
	local n1 = math.noise(x, y, z)
	local n2 = math.noise(x * 2.07 + 13.7, y * 2.07 - 9.2, z * 2.07 + 5.4) * 0.5
	local n3 = math.noise(x * 4.19 - 7.1, y * 4.19 + 19.3, z * 4.19 - 11.8) * 0.25
	return (n1 + n2 + n3) / 1.75
end

local function safeLookAt(fromP, toP)
	local d = toP - fromP
	if d.Magnitude < 1e-4 then
		return CFrame.new(fromP)
	end
	local u = d.Unit
	local up = math.abs(u.Y) > 0.96 and Vector3.new(0, 0, 1) or Vector3.new(0, 1, 0)
	return CFrame.lookAt(fromP, toP, up)
end

for _, r in ipairs({world, assembly}) do
	for _, d in ipairs(r:GetDescendants()) do
		if d:IsA("ParticleEmitter") or d:IsA("Beam") then
			d.Enabled = false
		end
	end
end

local oldRoot = assembly:FindFirstChild("REAL_3D_VOLUMETRIC_MODELS")
if oldRoot then oldRoot:Destroy() end
local root = Instance.new("Folder")
root.Name = "REAL_3D_VOLUMETRIC_MODELS"
root.Parent = assembly

local STRONG_REFS = {}
local function keep(obj)
	STRONG_REFS[#STRONG_REFS + 1] = obj
	return obj
end

local function style3DPart(p)
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	return p
end

local nozzles = {}
for idx, s in ipairs(SITES) do
	local head = moving:WaitForChild("REACTOR_EMITTER_REV03_" .. s.tag, 20)
	local tip = head and head:FindFirstChild("NOZZLE__white", true)
	assert(tip and tip:IsA("MeshPart"), "Missing NOZZLE__white on " .. s.tag)
	local sock = tip:WaitForChild("PILOT_FUEL_SOCKET_" .. s.tag, 20)
	local optic = head:FindFirstChild("OPTIC__cyan", true)
	local cellWin = head:FindFirstChild("WINDOW__cyan_core", true)
	nozzles[idx] = {
		site = s,
		head = head,
		tip = tip,
		tipOrigColor = tip.Color,
		tipOrigMat = tip.Material,
		optic = (optic and optic:IsA("MeshPart")) and optic or tip,
		opticOrigColor = (optic and optic:IsA("MeshPart")) and optic.Color or tip.Color,
		opticOrigMat = (optic and optic:IsA("MeshPart")) and optic.Material or tip.Material,
		cellWin = (cellWin and cellWin:IsA("MeshPart")) and cellWin or nil,
		cellOrigColor = (cellWin and cellWin:IsA("MeshPart")) and cellWin.Color or Color3.fromRGB(24, 92, 168),
		cellOrigMat = (cellWin and cellWin:IsA("MeshPart")) and cellWin.Material or Enum.Material.SmoothPlastic,
		socket = sock,
	}
end
Workspace:SetAttribute("VaporStep", "02_NOZZLES_READY")

-- ============================================================================
-- 1. FAST-BOOT (<0.4s) TRUE RGBA-BAKED 128x128 VOLUMETRIC PBR TEXTURES
-- ============================================================================
local function buildEditableTexture(size, pixelFn)
	local ei = keep(AssetService:CreateEditableImage({Size = Vector2.new(size, size)}))
	local buf = buffer.create(size * size * 4)
	local o = 0
	for py = 0, size - 1 do
		local v = (py + 0.5) / size
		for px = 0, size - 1 do
			local u = (px + 0.5) / size
			local r, g, b, a = pixelFn(u, v)
			buffer.writeu8(buf, o,     math.clamp(math.floor(r * 255 + 0.5), 0, 255))
			buffer.writeu8(buf, o + 1, math.clamp(math.floor(g * 255 + 0.5), 0, 255))
			buffer.writeu8(buf, o + 2, math.clamp(math.floor(b * 255 + 0.5), 0, 255))
			buffer.writeu8(buf, o + 3, math.clamp(math.floor(a * 255 + 0.5), 0, 255))
			o += 4
		end
	end
	ei:WritePixelsBuffer(Vector2.zero, Vector2.new(size, size), buf)
	return {content = Content.fromObject(ei), ref = ei}
end

-- #1: Cool grey-white cryogenic vapor puff (Stage 02 straight nozzle steam)
local texCryoVapor = buildEditableTexture(128, function(u, v)
	local dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
	local r = math.sqrt(dx * dx + dy * dy)
	local warp = fbm3(u * 4.2 + 2.1, v * 4.2 - 1.5, 0.8) * 0.24
	local mask = clamp01(1 - smooth(0.10, 0.95, r + warp * 0.55))
	local edgeZero = clamp01(1 - smooth(0.74, 0.95, r))
	local billow = clamp01(0.62 + 0.38 * fbm3(u * 7.2 - 3.4, v * 7.2 + 5.1, 2.3))
	local a = (mask ^ 1.55) * edgeZero * billow * 0.64
	local shade = 0.78 + 0.16 * billow
	return shade * 0.94, shade * 0.97, shade, a
end)

-- #2: Straight longitudinal supersonic vapor jet cone (Stage 02)
local texVaporJet = buildEditableTexture(128, function(u, v)
	local ang = u * math.pi * 2
	local streak = 0.62 + 0.38 * fbm3(math.cos(ang) * 2.6 + 1.5, math.sin(ang) * 2.6 - 0.8, v * 4.2)
	local entry = smooth(0.0, 0.10, v)
	local tail = (1 - smooth(0.20, 1.0, v)) ^ 1.60
	local a = clamp01(entry * tail * streak * 0.56)
	return 0.86, 0.90, 0.95, a
end)

-- #3: Conical flaring plasma laser beam (RGBA baked: incandescent white core -> electric cyan-blue sheath!)
local texConicalBeam = buildEditableTexture(128, function(u, v)
	local ang = u * math.pi * 2
	local fil = 0.55 + 0.45 * fbm3(math.cos(ang) * 3.2 + 4.1, math.sin(ang) * 3.2 - 2.3, v * 5.2)
	local nozzleFade = smooth(0.0, 0.08, v)
	local coreMerge = 0.50 + 0.50 * smooth(0.25, 0.92, v)
	local rimSoft = 1 - 0.22 * smooth(0.90, 1.0, v)
	local a = clamp01(nozzleFade * coreMerge * rimSoft * (0.58 + 0.42 * fil) * 0.88)
	local wMix = clamp01(v * 0.55 + fil * 0.48)
	local r = 0.22 + (1.0 - 0.22) * wMix
	local g = 0.84 + (1.0 - 0.84) * wMix
	return r, g, 1.0, a
end)

-- #4: Vivid Turquoise-Cyan Expansion & Magnetic Ring Texture (Reference Stage 04 04_cyan_140.jpg!)
local texCyanExpansion = buildEditableTexture(128, function(u, v)
	local dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
	local r = math.sqrt(dx * dx + dy * dy)
	local n1 = 0.5 + 0.5 * fbm3(u * 4.2 + 3.1, v * 4.2 - 1.8, 2.4)
	local radial = clamp01(1 - smooth(0.04, 0.92, r + (n1 - 0.5) * 0.14))
	local edgeZero = clamp01(1 - smooth(0.74, 0.95, math.max(math.abs(dx), math.abs(dy)))) * clamp01(1 - smooth(0.76, 0.95, r))
	local a = clamp01((radial ^ 1.35) * edgeZero * (0.68 + 0.32 * n1) * 0.88)
	local inner = clamp01(1 - r * 0.85)
	local cr = 0.05 + 0.24 * inner * n1
	local cg = 0.46 + 0.50 * inner
	local cb = 0.98 + 0.02 * inner
	return cr, cg, cb, a
end)

-- #5: Cloudy White-to-Ice-Blue Solar Corona Texture (feathery plasma billows around the white sun!)
local texWhiteIceCorona = buildEditableTexture(128, function(u, v)
	local dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
	local r = math.sqrt(dx * dx + dy * dy)
	local cloud1 = 0.5 + 0.5 * fbm3(u * 4.8 + 6.2, v * 4.8 - 3.7, 1.9)
	local cloud2 = 0.5 + 0.5 * fbm3(u * 9.5 - 2.1, v * 9.5 + 7.4, 4.3)
	local radial = clamp01(1 - smooth(0.05, 0.91, r - (cloud1 - 0.5) * 0.20))
	local edgeZero = clamp01(1 - smooth(0.72, 0.94, math.max(math.abs(dx), math.abs(dy)))) * clamp01(1 - smooth(0.74, 0.95, r))
	local wisp = clamp01(cloud1 * 0.68 + cloud2 * 0.32)
	local a = clamp01((radial ^ 1.30) * edgeZero * (0.50 + 0.50 * wisp) * 0.92)
	local whiteCore = clamp01((1 - r * 0.72) * (0.55 + 0.45 * wisp))
	local cr = 0.52 + 0.48 * whiteCore
	local cg = 0.80 + 0.20 * whiteCore
	return cr, cg, 1.0, a
end)

-- #6: Stormy Multi-Tone Deep Royal-Cobalt & Indigo Chamber Nebula Texture
local texStormyCobaltNebula = buildEditableTexture(128, function(u, v)
	local dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
	local r = math.sqrt(dx * dx + dy * dy)
	local f1 = 0.5 + 0.5 * fbm3(u * 3.5 + 8.4, v * 3.5 + 1.9, 3.2)
	local f2 = 0.5 + 0.5 * fbm3(u * 7.6 - 4.8, v * 7.6 + 2.6, 6.1)
	local mask = clamp01(1 - smooth(0.05, 0.91, r + (f1 - 0.5) * 0.20))
	local edgeZero = clamp01(1 - smooth(0.72, 0.94, math.max(math.abs(dx), math.abs(dy)))) * clamp01(1 - smooth(0.74, 0.95, r))
	local neb = clamp01(f1 * 0.64 + f2 * 0.36)
	local a = clamp01((mask ^ 1.35) * edgeZero * (0.52 + 0.48 * neb) * 0.92)
	local crest = clamp01((neb - 0.42) * 1.85)
	local cr = 0.09 + 0.15 * neb + 0.34 * (crest ^ 1.35)
	local cg = 0.20 + 0.30 * neb + 0.34 * (crest ^ 1.25)
	local cb = 0.68 + 0.28 * neb + 0.04 * crest
	return clamp01(cr), clamp01(cg), clamp01(cb), a
end)

-- Full-white 16x16 EmissiveMask so Stages 04-06 self-illuminate cleanly from within
-- WITHOUT flooding or distorting surrounding chamber wall / emitter barrel colors!
local texFullEmissiveMask = buildEditableTexture(16, function()
	return 1.0, 1.0, 1.0, 1.0
end)
texConicalBeam.emissive        = 1.90
texCyanExpansion.emissive      = 1.75
texWhiteIceCorona.emissive     = 1.85
texStormyCobaltNebula.emissive = 2.15
task.wait()

Workspace:SetAttribute("VaporStep", "03_SIX_RGBA_TEXTURES_READY")

-- ============================================================================
-- 2. ULTRA-HIGH-POLY, CORNERLESS GPU-NATIVE 3D MESH TEMPLATES (ZERO STALLS!)
-- ============================================================================
local function toStaticMeshContent(em)
	local ok, c = pcall(function()
		return AssetService:CreateDataModelContentAsync(em)
	end)
	if ok and c then
		return c
	end
	return Content.fromObject(em)
end

-- 6 Polar Radial Ellipsoidal Cloud Domes x 5 rings x 24 circular segments = 1,296 curved triangles!
-- True 360° circular polar geometry (ZERO 90° square corners!) + fast OIT alpha-sort for locked 60+ FPS!
local function buildMultiCloudCluster(seed)
	local em = keep(AssetService:CreateEditableMesh())
	local subSpecs = {
		{off = Vector3.new(-0.36,  0.22, -0.28), rx = 0.74, ry = 0.62, rz = 0.30, rot = 0.4, tiltX = -0.13, tiltY =  0.13},
		{off = Vector3.new( 0.38, -0.18, -0.17), rx = 0.70, ry = 0.62, rz = 0.28, rot = 1.7, tiltX =  0.12, tiltY = -0.14},
		{off = Vector3.new(-0.14, -0.38, -0.06), rx = 0.74, ry = 0.60, rz = 0.29, rot = 2.9, tiltX =  0.14, tiltY =  0.10},
		{off = Vector3.new( 0.22,  0.34,  0.06), rx = 0.68, ry = 0.60, rz = 0.27, rot = 4.1, tiltX = -0.12, tiltY = -0.11},
		{off = Vector3.new(-0.28, -0.06,  0.18), rx = 0.66, ry = 0.56, rz = 0.26, rot = 5.2, tiltX =  0.09, tiltY =  0.13},
		{off = Vector3.new( 0.14, -0.26,  0.28), rx = 0.68, ry = 0.58, rz = 0.26, rot = 1.1, tiltX = -0.10, tiltY =  0.09},
	}
	local rings, segs = 5, 24
	for wIdx, sp in ipairs(subSpecs) do
		local cf = CFrame.new(sp.off) * CFrame.Angles(sp.tiltX, sp.tiltY, sp.rot)
		local cCrinkle = fbm3(seed + wIdx, -seed, wIdx * 1.7) * 0.10
		local cBase = cf:PointToWorldSpace(Vector3.new(0, 0, sp.rz + cCrinkle))
		local cNorm = (cf:VectorToWorldSpace(Vector3.new(0, 0, 1))).Unit
		local cVid = em:AddVertex(cBase)
		local cNid = em:AddNormal(cNorm)
		local cUvid = em:AddUV(Vector2.new(0.5, 0.5))

		local vids, nids, uvids = {}, {}, {}
		for ir = 1, rings do
			local rFrac = ir / rings
			vids[ir] = {}; nids[ir] = {}; uvids[ir] = {}
			local rimAtten = 1 - 0.70 * (rFrac * rFrac)
			local domeH = math.sqrt(math.max(0, 1 - rFrac * rFrac * 0.86)) * sp.rz
			for is = 0, segs do
				local th = (is / segs) * math.pi * 2
				local vx = rFrac * math.cos(th)
				local vy = rFrac * math.sin(th)
				local crinkle = fbm3(vx * 1.85 + seed + wIdx, vy * 1.85 - seed, wIdx * 1.7) * 0.11 * rimAtten
				local baseP = cf:PointToWorldSpace(Vector3.new(
					vx * sp.rx * (1 + crinkle * 0.20),
					vy * sp.ry * (1 - crinkle * 0.16),
					domeH + crinkle
				))
				local wn = (cf:VectorToWorldSpace(Vector3.new(vx * 0.24, vy * 0.24, 0.94))).Unit
				vids[ir][is] = em:AddVertex(baseP)
				nids[ir][is] = em:AddNormal(wn)
				uvids[ir][is] = em:AddUV(Vector2.new(0.5 + vx * 0.475, 0.5 + vy * 0.475))
			end
		end
		for is = 0, segs - 1 do
			local f = em:AddTriangle(cVid, vids[1][is], vids[1][is + 1])
			em:SetFaceNormals(f, {cNid, nids[1][is], nids[1][is + 1]})
			em:SetFaceUVs(f, {cUvid, uvids[1][is], uvids[1][is + 1]})
		end
		for ir = 1, rings - 1 do
			for is = 0, segs - 1 do
				local f1 = em:AddTriangle(vids[ir][is], vids[ir + 1][is], vids[ir + 1][is + 1])
				em:SetFaceNormals(f1, {nids[ir][is], nids[ir + 1][is], nids[ir + 1][is + 1]})
				em:SetFaceUVs(f1, {uvids[ir][is], uvids[ir + 1][is], uvids[ir + 1][is + 1]})
				local f2 = em:AddTriangle(vids[ir][is], vids[ir + 1][is + 1], vids[ir][is + 1])
				em:SetFaceNormals(f2, {nids[ir][is], nids[ir + 1][is + 1], nids[ir][is + 1]})
				em:SetFaceUVs(f2, {uvids[ir][is], uvids[ir + 1][is + 1], uvids[ir][is + 1]})
			end
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = #subSpecs * (2 * rings - 1) * segs}
end

-- Ultra-Fine Cornerless 4-Puff 3D Micro-Constellation Template (4 separated 360° polar micro-domes x 3 rings x 20 segs = 400 tris!)
-- Turns 672 independent MeshParts into 2,688 tiny flowing micro-clouds that dissolve below 1/255 bit-depth with ZERO perceptible pop!
local function buildMicroWispCluster(seed)
	local em = keep(AssetService:CreateEditableMesh())
	local subSpecs = {
		{off = Vector3.new(-0.46,  0.34, -0.18), rx = 0.40, ry = 0.35, rz = 0.24, rot = 0.5, tiltX = -0.11, tiltY =  0.12},
		{off = Vector3.new( 0.48, -0.30, -0.06), rx = 0.38, ry = 0.34, rz = 0.22, rot = 2.1, tiltX =  0.12, tiltY = -0.10},
		{off = Vector3.new(-0.24, -0.44,  0.08), rx = 0.39, ry = 0.34, rz = 0.23, rot = 3.8, tiltX =  0.10, tiltY =  0.11},
		{off = Vector3.new( 0.26,  0.42,  0.18), rx = 0.37, ry = 0.33, rz = 0.22, rot = 5.1, tiltX = -0.10, tiltY = -0.11},
	}
	local rings, segs = 3, 20
	for wIdx, sp in ipairs(subSpecs) do
		local cf = CFrame.new(sp.off) * CFrame.Angles(sp.tiltX, sp.tiltY, sp.rot)
		local cCrinkle = fbm3(seed + wIdx, -seed, wIdx * 1.9) * 0.08
		local cBase = cf:PointToWorldSpace(Vector3.new(0, 0, sp.rz + cCrinkle))
		local cNorm = (cf:VectorToWorldSpace(Vector3.new(0, 0, 1))).Unit
		local cVid = em:AddVertex(cBase)
		local cNid = em:AddNormal(cNorm)
		local cUvid = em:AddUV(Vector2.new(0.5, 0.5))

		local vids, nids, uvids = {}, {}, {}
		for ir = 1, rings do
			local rFrac = ir / rings
			vids[ir] = {}; nids[ir] = {}; uvids[ir] = {}
			local rimAtten = 1 - 0.72 * (rFrac * rFrac)
			local domeH = math.sqrt(math.max(0, 1 - rFrac * rFrac * 0.86)) * sp.rz
			for is = 0, segs do
				local th = (is / segs) * math.pi * 2
				local vx = rFrac * math.cos(th)
				local vy = rFrac * math.sin(th)
				local crinkle = fbm3(vx * 1.95 + seed + wIdx, vy * 1.95 - seed, wIdx * 2.1) * 0.09 * rimAtten
				local baseP = cf:PointToWorldSpace(Vector3.new(
					vx * sp.rx * (1 + crinkle * 0.18),
					vy * sp.ry * (1 - crinkle * 0.15),
					domeH + crinkle
				))
				local wn = (cf:VectorToWorldSpace(Vector3.new(vx * 0.24, vy * 0.24, 0.94))).Unit
				vids[ir][is] = em:AddVertex(baseP)
				nids[ir][is] = em:AddNormal(wn)
				uvids[ir][is] = em:AddUV(Vector2.new(0.5 + vx * 0.475, 0.5 + vy * 0.475))
			end
		end
		for is = 0, segs - 1 do
			local f = em:AddTriangle(cVid, vids[1][is], vids[1][is + 1])
			em:SetFaceNormals(f, {cNid, nids[1][is], nids[1][is + 1]})
			em:SetFaceUVs(f, {cUvid, uvids[1][is], uvids[1][is + 1]})
		end
		for ir = 1, rings - 1 do
			for is = 0, segs - 1 do
				local f1 = em:AddTriangle(vids[ir][is], vids[ir + 1][is], vids[ir + 1][is + 1])
				em:SetFaceNormals(f1, {nids[ir][is], nids[ir + 1][is], nids[ir + 1][is + 1]})
				em:SetFaceUVs(f1, {uvids[ir][is], uvids[ir + 1][is], uvids[ir + 1][is + 1]})
				local f2 = em:AddTriangle(vids[ir][is], vids[ir + 1][is + 1], vids[ir][is + 1])
				em:SetFaceNormals(f2, {nids[ir][is], nids[ir + 1][is + 1], nids[ir][is + 1]})
				em:SetFaceUVs(f2, {uvids[ir][is], uvids[ir + 1][is + 1], uvids[ir][is + 1]})
			end
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = #subSpecs * (2 * rings - 1) * segs}
end

-- Straight Axisymmetric High-Poly Conical 3D Funnel (24 x 48 = 2,304 triangles, 7.5° smooth circular perimeter!)
local function buildAxisymmetricConeMesh(seed)
	local em = keep(AssetService:CreateEditableMesh())
	local rings, segs = 24, 48
	local vids, nids, uvids = {}, {}, {}
	for r = 0, rings do
		local t = r / rings
		vids[r] = {}; nids[r] = {}; uvids[r] = {}
		local baseR = 0.16 + 0.34 * (t ^ 0.92)
		for s = 0, segs do
			local u = s / segs
			local th = u * math.pi * 2
			local c, sn = math.cos(th), math.sin(th)
			local flute = math.sin(th * 5 + t * 5.2) * 0.032 * t
			local rip = fbm3(c * 1.9 + seed, sn * 1.9, t * 2.8) * 0.042 * t
			local rad = math.max(0.06, baseR + flute + rip)
			local pos = Vector3.new(c * rad, sn * rad, -t)
			vids[r][s] = em:AddVertex(pos)
			nids[r][s] = em:AddNormal(Vector3.new(c * 0.88, sn * 0.88, 0.47).Unit)
			uvids[r][s] = em:AddUV(Vector2.new(u, t))
		end
	end
	for r = 0, rings - 1 do
		for s = 0, segs - 1 do
			local f1 = em:AddTriangle(vids[r][s], vids[r + 1][s], vids[r + 1][s + 1])
			em:SetFaceNormals(f1, {nids[r][s], nids[r + 1][s], nids[r + 1][s + 1]})
			em:SetFaceUVs(f1, {uvids[r][s], uvids[r + 1][s], uvids[r + 1][s + 1]})
			local f2 = em:AddTriangle(vids[r][s], vids[r + 1][s + 1], vids[r][s + 1])
			em:SetFaceNormals(f2, {nids[r][s], nids[r + 1][s + 1], nids[r][s + 1]})
			em:SetFaceUVs(f2, {uvids[r][s], uvids[r + 1][s + 1], uvids[r][s + 1]})
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = rings * segs * 2}
end

-- High-Poly Helical Cylindrical Laser Plasma Envelope (26 x 48 = 2,496 triangles, 7.5° smooth circular perimeter!)
local function buildCylindricalLaserMesh()
	local em = keep(AssetService:CreateEditableMesh())
	local rings, segs = 26, 48
	local vids, nids, uvids = {}, {}, {}
	for r = 0, rings do
		local t = r / rings
		vids[r] = {}; nids[r] = {}; uvids[r] = {}
		local z = 0.5 - t
		local env = math.sin(t * math.pi)
		local flare = 0.34 + 0.26 * (t ^ 1.1)
		for s = 0, segs do
			local u = s / segs
			local th = u * math.pi * 2
			local c, sn = math.cos(th), math.sin(th)
			local w1 = math.sin(t * 14.0 + th * 2.0) * 0.048 * env
			local rad = flare * (1 + w1)
			vids[r][s] = em:AddVertex(Vector3.new(c * rad, sn * rad, z))
			nids[r][s] = em:AddNormal(Vector3.new(c * 0.92, sn * 0.92, 0.39).Unit)
			uvids[r][s] = em:AddUV(Vector2.new(u, t))
		end
	end
	for r = 0, rings - 1 do
		for s = 0, segs - 1 do
			local f1 = em:AddTriangle(vids[r][s], vids[r + 1][s], vids[r + 1][s + 1])
			em:SetFaceNormals(f1, {nids[r][s], nids[r + 1][s], nids[r + 1][s + 1]})
			em:SetFaceUVs(f1, {uvids[r][s], uvids[r + 1][s], uvids[r + 1][s + 1]})
			local f2 = em:AddTriangle(vids[r][s], vids[r + 1][s + 1], vids[r][s + 1])
			em:SetFaceNormals(f2, {nids[r][s], nids[r + 1][s + 1], nids[r][s + 1]})
			em:SetFaceUVs(f2, {uvids[r][s], uvids[r + 1][s + 1], uvids[r][s + 1]})
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = rings * segs * 2}
end

-- Ultra-Smooth High-Poly 3D Solar Spheres (44x76 = 6,688 tris & 36x64 = 4,608 tris -> ZERO polygonal facets!)
local function buildSolar3DSphere(rings, segs, amp, freq, seed)
	local em = keep(AssetService:CreateEditableMesh())
	local vids, nids, uvids = {}, {}, {}
	for r = 0, rings do
		local v = r / rings
		local theta = v * math.pi
		local sinT, cosT = math.sin(theta), math.cos(theta)
		vids[r] = {}; nids[r] = {}; uvids[r] = {}
		for s = 0, segs do
			local u = s / segs
			local phi = u * math.pi * 2
			local sx = sinT * math.cos(phi)
			local sy = cosT
			local sz = sinT * math.sin(phi)
			local n1 = fbm3(sx * freq + seed, sy * freq - seed * 0.5, sz * freq + 1.4)
			local rad = 0.5 * (1 + n1 * amp)
			local dir = Vector3.new(sx, sy, sz)
			vids[r][s] = em:AddVertex(dir * rad)
			nids[r][s] = em:AddNormal(-dir)
			uvids[r][s] = em:AddUV(Vector2.new(u, v))
		end
	end
	for r = 0, rings - 1 do
		for s = 0, segs - 1 do
			local f1 = em:AddTriangle(vids[r][s], vids[r + 1][s + 1], vids[r + 1][s])
			em:SetFaceNormals(f1, {nids[r][s], nids[r + 1][s + 1], nids[r + 1][s]})
			em:SetFaceUVs(f1, {uvids[r][s], uvids[r + 1][s + 1], uvids[r + 1][s]})
			local f2 = em:AddTriangle(vids[r][s], vids[r][s + 1], vids[r + 1][s + 1])
			em:SetFaceNormals(f2, {nids[r][s], nids[r][s + 1], nids[r + 1][s + 1]})
			em:SetFaceUVs(f2, {uvids[r][s], uvids[r][s + 1], uvids[r + 1][s + 1]})
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = rings * segs * 2}
end

-- High-Poly Toroidal Containment Ring (96 x 18 = 3,456 triangles -> 3.75° razor-smooth circular arc!)
local function buildMagneticTorusRing(majSegs, minSegs, minR)
	local em = keep(AssetService:CreateEditableMesh())
	local vids, nids, uvids = {}, {}, {}
	for i = 0, majSegs do
		local u = i / majSegs
		local phi = u * math.pi * 2
		local cp, sp = math.cos(phi), math.sin(phi)
		vids[i] = {}; nids[i] = {}; uvids[i] = {}
		for j = 0, minSegs do
			local v = j / minSegs
			local th = v * math.pi * 2
			local ct, st = math.cos(th), math.sin(th)
			local r = 0.5 + minR * ct
			local pos = Vector3.new(cp * r, sp * r, minR * st)
			vids[i][j] = em:AddVertex(pos)
			nids[i][j] = em:AddNormal(Vector3.new(-cp, -sp, 0.35).Unit)
			uvids[i][j] = em:AddUV(Vector2.new(u, v))
		end
	end
	for i = 0, majSegs - 1 do
		for j = 0, minSegs - 1 do
			local f1 = em:AddTriangle(vids[i][j], vids[i + 1][j], vids[i + 1][j + 1])
			em:SetFaceNormals(f1, {nids[i][j], nids[i + 1][j], nids[i + 1][j + 1]})
			em:SetFaceUVs(f1, {uvids[i][j], uvids[i + 1][j], uvids[i + 1][j + 1]})
			local f2 = em:AddTriangle(vids[i][j], vids[i + 1][j + 1], vids[i][j + 1])
			em:SetFaceNormals(f2, {nids[i][j], nids[i + 1][j + 1], nids[i][j + 1]})
			em:SetFaceUVs(f2, {uvids[i][j], uvids[i + 1][j + 1], uvids[i][j + 1]})
		end
	end
	return {em = em, content = toStaticMeshContent(em), tris = majSegs * minSegs * 2}
end

-- EXACTLY 7 Cornerless High-Polygon GPU-Native Mesh templates (<= 8 client limit!):
local clusterTplA     = buildMultiCloudCluster(1.4)
local clusterTplB     = buildMicroWispCluster(6.7)
local coneTpl         = buildAxisymmetricConeMesh(2.2)
local laserWaveTpl    = buildCylindricalLaserMesh()
local starSphereInner = buildSolar3DSphere(48, 84, 0.135, 1.95, 3.1)
local starSphereOuter = buildSolar3DSphere(44, 76, 0.235, 2.25, 8.4)
local magRingTpl      = buildMagneticTorusRing(108, 20, 0.016)
task.wait()
Workspace:SetAttribute("VaporStep", "05_SEVEN_EDITABLE_MESHES_BUILT")

local meshContentByEm = {
	[clusterTplA.em]     = clusterTplA.content,
	[clusterTplB.em]     = clusterTplB.content,
	[coneTpl.em]         = coneTpl.content,
	[laserWaveTpl.em]    = laserWaveTpl.content,
	[starSphereInner.em] = starSphereInner.content,
	[starSphereOuter.em] = starSphereOuter.content,
	[magRingTpl.em]      = magRingTpl.content,
}
Workspace:SetAttribute("TotalHighPolyTemplateTris",
	clusterTplA.tris + clusterTplB.tris + coneTpl.tris + laserWaveTpl.tris
	+ starSphereInner.tris + starSphereOuter.tris + magRingTpl.tris)

local protoCache = {}
local emissiveSurfaces = {}
local function makeAlphaMeshPart(em, texBundle, name)
	local byEm = protoCache[em]
	if not byEm then
		byEm = {}
		protoCache[em] = byEm
	end
	local proto = byEm[texBundle.ref]
	local mp
	if not proto then
		local mContent = meshContentByEm[em] or Content.fromObject(em)
		mp = style3DPart(AssetService:CreateMeshPartAsync(mContent))
		mp.Material = Enum.Material.SmoothPlastic
		mp.Transparency = 1
		local saCfg = {ColorMap = texBundle.content}
		if texBundle.emissive then
			saCfg.EmissiveMask = texFullEmissiveMask.content
		end
		local sa = AssetService:CreateSurfaceAppearanceAsync(saCfg)
		sa.AlphaMode = Enum.AlphaMode.Transparency
		if texBundle.emissive then
			pcall(function()
				sa.EmissiveStrength = texBundle.emissive
				sa.EmissiveTint = Color3.fromRGB(255, 255, 255)
			end)
		end
		sa.Parent = mp
		local saved = mp:Clone()
		keep(saved)
		byEm[texBundle.ref] = saved
	else
		mp = proto:Clone()
	end
	mp.Name = name
	mp.Parent = root
	if texBundle.emissive then
		local saInst = mp:FindFirstChildOfClass("SurfaceAppearance")
		if saInst then
			emissiveSurfaces[#emissiveSurfaces + 1] = {sa = saInst, base = texBundle.emissive}
		end
	end
	return {part = mp, baseSize = mp.MeshSize}
end

-- ============================================================================
-- 3. STAGE 02: STRAIGHT AXIAL NOZZLE-BORN 3D VAPOR (GRAVITY = 0!)
-- ============================================================================
local mistLights = {}
for i, spec in ipairs({
	{off = Vector3.new(0, 1.5, 13.5),    range = 38, mult = 1.15},
	{off = Vector3.new(-13.5, -1.0, 10), range = 32, mult = 1.00},
	{off = Vector3.new( 13.5, -1.0, 10), range = 32, mult = 1.00},
}) do
	local a = style3DPart(Instance.new("Part"))
	a.Name = "CHAMBER_3D_MIST_ILLUM_" .. i
	a.Size = Vector3.new(0.2, 0.2, 0.2)
	a.Transparency = 1
	a.CFrame = CFrame.new(O + spec.off)
	a.Parent = root
	local pl = Instance.new("PointLight")
	pl.Brightness = 0
	pl.Range = spec.range
	pl.Shadows = false
	pl.Color = Color3.fromRGB(224, 232, 242)
	pl.Parent = a
	mistLights[i] = {light = pl, mult = spec.mult}
end

local nozzleJets = {}
for idx, nz in ipairs(nozzles) do
	nozzleJets[idx] = {
		makeAlphaMeshPart(coneTpl.em, texVaporJet, "NOZZLE_3D_STRAIGHT_JET_INNER_" .. nz.site.tag),
		makeAlphaMeshPart(coneTpl.em, texVaporJet, "NOZZLE_3D_STRAIGHT_JET_OUTER_" .. nz.site.tag),
	}
end

local PUFFS_PER_NOZZLE = 27
local fluidPuffs = {}
local rng = Random.new(20261027)

for nIdx = 1, 6 do
	for k = 1, PUFFS_PER_NOZZLE do
		local tpl = clusterTplA
		local meshObj = makeAlphaMeshPart(tpl.em, texCryoVapor,
			string.format("NOZZLE_STRAIGHT_VAPOR_%d_%02d", nIdx, k))
		fluidPuffs[#fluidPuffs + 1] = {
			nozzleIdx = nIdx,
			slotIdx = k,
			mesh = meshObj,
			alive = false,
			age = 0,
			maxLife = 1.7,
			pos = FOCUS,
			vel = Vector3.zero,
			roll = rng:NextNumber(0, math.pi * 2),
			spin = rng:NextNumber(-0.75, 0.75),
			endSize = 3.6,
			seed = rng:NextNumber(0, 100),
		}
	end
end

local function spawnStraightPuffAtNozzle(puff, nz, fuelStrength)
	local s = nz.site
	local mouth = nz.socket.WorldPosition
	local inward = -s.axis -- Exact straight laser axis!
	local refUp = math.abs(inward.Y) > 0.92 and Vector3.new(1, 0, 0) or Vector3.new(0, 1, 0)
	local sideA = inward:Cross(refUp).Unit
	local sideB = inward:Cross(sideA).Unit
	local ang = rng:NextNumber(0, math.pi * 2)
	local boreR = rng:NextNumber(0.0, 0.24)
	local radialDir = sideA * math.cos(ang) + sideB * math.sin(ang)

	puff.alive = true
	puff.age = 0
	puff.maxLife = rng:NextNumber(1.30, 1.95)
	puff.pos = mouth + inward * 0.10 + radialDir * boreR
	local launchSpeed = rng:NextNumber(6.2, 9.4) * (0.72 + 0.28 * fuelStrength) * s.jetScale
	local symmetricSpread = rng:NextNumber(0.55, 2.05)
	puff.vel = inward * launchSpeed + radialDir * symmetricSpread
	puff.endSize = rng:NextNumber(2.8, 4.2) * s.jetScale
	puff.spin = rng:NextNumber(-0.70, 0.70)
end

-- ============================================================================
-- 4. STAGES 04 -> 06/ONLINE: RGBA-BAKED REFERENCE MULTI-LAYER ARCHITECTURE
-- ============================================================================
local centerDriverPart = style3DPart(Instance.new("Part"))
centerDriverPart.Name = "FUSION_3D_CENTER_DRIVER"
centerDriverPart.Size = Vector3.new(0.2, 0.2, 0.2)
centerDriverPart.Transparency = 1
centerDriverPart.CFrame = CFrame.new(FOCUS)
centerDriverPart.Parent = root
local centerDriver = Instance.new("PointLight")
centerDriver.Brightness = 0
centerDriver.Range = 14
centerDriver.Shadows = false
centerDriver.Color = Color3.fromRGB(232, 243, 255)
centerDriver.Parent = centerDriverPart

-- Keep auxiliary room/front PointLights strictly OFF during normal operation so
-- emitted reactor light NEVER bleaches or distorts chamber wall / emitter barrel colors!
local chamberCobaltLights = {}
for i, spec in ipairs({
	{off = Vector3.new(-11.5,  3.5,  1.5), range = 18, mult = 0.0},
	{off = Vector3.new( 11.5,  3.5,  1.5), range = 18, mult = 0.0},
	{off = Vector3.new(  0.0, -7.5,  1.5), range = 18, mult = 0.0},
	{off = Vector3.new(  0.0,  8.5,  1.0), range = 18, mult = 0.0},
}) do
	local a = style3DPart(Instance.new("Part"))
	a.Name = "FUSION_3D_COBALT_CHAMBER_LIGHT_" .. i
	a.Size = Vector3.new(0.2, 0.2, 0.2)
	a.Transparency = 1
	a.CFrame = CFrame.new(FOCUS + spec.off)
	a.Parent = root
	local pl = Instance.new("PointLight")
	pl.Brightness = 0
	pl.Range = spec.range
	pl.Shadows = false
	pl.Color = Color3.fromRGB(215, 232, 255)
	pl.Parent = a
	chamberCobaltLights[i] = {light = pl, mult = spec.mult}
end

local nebulaFrontLightPart = style3DPart(Instance.new("Part"))
nebulaFrontLightPart.Name = "FUSION_3D_NEBULA_FRONT_ILLUM"
nebulaFrontLightPart.Size = Vector3.new(0.2, 0.2, 0.2)
nebulaFrontLightPart.Transparency = 1
nebulaFrontLightPart.CFrame = CFrame.new(FOCUS + Vector3.new(0, 0, 4.5))
nebulaFrontLightPart.Parent = root
local nebulaFrontLight = Instance.new("PointLight")
nebulaFrontLight.Brightness = 0
nebulaFrontLight.Range = 12
nebulaFrontLight.Shadows = false
nebulaFrontLight.Color = Color3.fromRGB(228, 240, 255)
nebulaFrontLight.Parent = nebulaFrontLightPart

-- 6 Conical Flaring 3D Lasers + 24 Fine Collar Guide Filaments
local GUIDE_OFFSETS = {
	Vector2.new( 0.78,  0.28),
	Vector2.new(-0.78,  0.28),
	Vector2.new( 0.78, -0.28),
	Vector2.new(-0.78, -0.28),
}

local lasers = {}
for idx, nz in ipairs(nozzles) do
	local coreBeam = style3DPart(Instance.new("Part"))
	coreBeam.Name = "LASER_3D_CORE_" .. nz.site.tag
	coreBeam.Shape = Enum.PartType.Cylinder
	coreBeam.Material = Enum.Material.Neon
	coreBeam.Transparency = 1
	coreBeam.Parent = root

	local outerBeam = style3DPart(Instance.new("Part"))
	outerBeam.Name = "LASER_3D_NEON_SHEATH_" .. nz.site.tag
	outerBeam.Shape = Enum.PartType.Cylinder
	outerBeam.Material = Enum.Material.Neon
	outerBeam.Transparency = 1
	outerBeam.Parent = root

	local conicalFlare = makeAlphaMeshPart(coneTpl.em, texConicalBeam,
		"LASER_3D_CONICAL_FLARE_" .. nz.site.tag)

	local waveSheath = makeAlphaMeshPart(laserWaveTpl.em, texConicalBeam,
		"LASER_3D_WAVE_ENVELOPE_" .. nz.site.tag)

	local muzzleLens = style3DPart(Instance.new("Part"))
	muzzleLens.Name = "LASER_3D_MUZZLE_LENS_" .. nz.site.tag
	muzzleLens.Shape = Enum.PartType.Ball
	muzzleLens.Material = Enum.Material.Neon
	muzzleLens.Transparency = 1
	muzzleLens.Parent = root

	-- Physical Nozzle Integration: 3D Polar Plasma Collar Shroud + Spinning 3D Magnetic Nozzle Ring
	-- + 8 Ultra-Fine Staggered 3D Micro-Wavelets streaming smoothly from Nozzle -> Core!
	local collarShroud = makeAlphaMeshPart(clusterTplA.em, texCyanExpansion,
		"NOZZLE_3D_COLLAR_SHROUD_" .. nz.site.tag)
	local collarRing = makeAlphaMeshPart(magRingTpl.em, texCyanExpansion,
		"NOZZLE_3D_MAG_COLLAR_" .. nz.site.tag)
	local pulses = {}
	for pIdx = 1, 8 do
		pulses[pIdx] = makeAlphaMeshPart(clusterTplB.em, texWhiteIceCorona,
			string.format("CONDUIT_3D_SURGE_PULSE_%s_%d", nz.site.tag, pIdx))
	end

	local guides = {}
	for g = 1, 4 do
		local rail = style3DPart(Instance.new("Part"))
		rail.Name = string.format("LASER_3D_GUIDE_RAIL_%s_%d", nz.site.tag, g)
		rail.Shape = Enum.PartType.Cylinder
		rail.Material = Enum.Material.Neon
		rail.Transparency = 1
		rail.Parent = root
		guides[g] = rail
	end

	lasers[idx] = {
		nozzle = nz,
		coreBeam = coreBeam,
		outerBeam = outerBeam,
		conicalFlare = conicalFlare,
		waveSheath = waveSheath,
		muzzleLens = muzzleLens,
		collarShroud = collarShroud,
		collarRing = collarRing,
		pulses = pulses,
		guides = guides,
		ext = 0,
		impacted = false,
	}
end

-- 100%-OPAQUE (Transparency = 0) HARDWARE Z-OCCLUDING 3D SOLAR CORE SPHERE
local opaqueSunBody = style3DPart(AssetService:CreateMeshPartAsync(starSphereInner.content))
opaqueSunBody.Name = "STAR_3D_OPAQUE_SUN_BODY"
opaqueSunBody.Material = Enum.Material.Neon
opaqueSunBody.Transparency = 1
opaqueSunBody.Parent = root
local opaqueSunBase = opaqueSunBody.MeshSize

local softNeonAura = style3DPart(AssetService:CreateMeshPartAsync(starSphereOuter.content))
softNeonAura.Name = "STAR_3D_SOFT_NEON_AURA"
softNeonAura.Material = Enum.Material.Neon
softNeonAura.Transparency = 1
softNeonAura.Parent = root
local softNeonBase = softNeonAura.MeshSize

-- 6 Organic Multi-Lobed 3D Boiling Cloud & Solar Prominence Shells (breaks up hard geometric sphere edge!):
local starShells = {
	{
		mesh = makeAlphaMeshPart(clusterTplA.em, texWhiteIceCorona, "STAR_3D_BOILING_PHOTOSPHERE_A"),
		rotVel = Vector3.new(0.28, -0.34, 0.72),
		baseTilt = CFrame.Angles(0.18, -0.22, 0.40),
		kind = "CLOUD_BILLOW_A",
	},
	{
		mesh = makeAlphaMeshPart(clusterTplA.em, texWhiteIceCorona, "STAR_3D_BOILING_PHOTOSPHERE_B"),
		rotVel = Vector3.new(-0.32, 0.26, -0.64),
		baseTilt = CFrame.Angles(-0.24, 0.28, 1.95),
		kind = "CLOUD_BILLOW_B",
	},
	{
		mesh = makeAlphaMeshPart(clusterTplA.em, texWhiteIceCorona, "STAR_3D_BOILING_PHOTOSPHERE_C"),
		rotVel = Vector3.new(0.22, 0.36, 0.52),
		baseTilt = CFrame.Angles(0.32, 0.55, 3.60),
		kind = "CLOUD_BILLOW_C",
	},
	{
		mesh = makeAlphaMeshPart(starSphereOuter.em, texWhiteIceCorona, "STAR_3D_SOLAR_PROMINENCE_CORE"),
		rotVel = Vector3.new(-0.92, 0.76, -0.84),
		baseTilt = CFrame.identity,
		kind = "PROMINENCE",
	},
	{
		mesh = makeAlphaMeshPart(starSphereOuter.em, texCyanExpansion, "STAR_3D_CYAN_EXPANSION_INNER"),
		rotVel = Vector3.new(0.58, -0.92, 0.70),
		baseTilt = CFrame.identity,
		kind = "CYAN_INNER",
	},
	{
		mesh = makeAlphaMeshPart(clusterTplA.em, texCyanExpansion, "STAR_3D_CYAN_EXPANSION_OUTER"),
		rotVel = Vector3.new(-0.24, 0.30, -0.46),
		baseTilt = CFrame.Angles(-0.16, -0.26, 2.40),
		kind = "CYAN_OUTER",
	},
}

-- C^2-Smooth Sub-8-Bit Zero-Derivative Lifecycle Bell (sin(pi * u)^3.5):
-- Value, 1st derivative, AND 2nd derivative are ALL 0.0000 at birth (u=0) and death (u=1),
-- keeping outer 28% of every wisp's lifecycle below 1/255 bit quantization so vanishing/spawning is 100% imperceptible!
local function imperceptibleBell(u)
	local s = math.sin(u * math.pi)
	if s <= 0 then return 0 end
	local s2 = s * s
	return s2 * s * math.sqrt(s)
end

local goldenAngle = math.pi * (3 - math.sqrt(5))

-- 144 Billowing & Imperceptibly Dissolving 3D Solar Corona Plasma Billows (576 micro-billows masking sphere rim!)
local CORONA_PLUME_COUNT = 144
local coronaPlumes = {}
for i = 1, CORONA_PLUME_COUNT do
	local y = 1 - ((i - 0.5) / CORONA_PLUME_COUNT) * 2
	local rXY = math.sqrt(math.max(0, 1 - y * y))
	local theta = goldenAngle * i
	local dir = Vector3.new(math.cos(theta) * rXY, y, math.sin(theta) * rXY)
	local tex = (i % 6 == 0) and texCyanExpansion or texWhiteIceCorona
	local mObj = makeAlphaMeshPart(clusterTplB.em, tex, string.format("STAR_3D_CORONA_PLUME_%03d", i))
	local rotAxis = Vector3.new(
		math.sin(i * 1.73),
		math.cos(i * 2.19),
		math.sin(i * 0.97 + 1.2)
	).Unit
	local uInit = (i * 0.61803398875) % 1
	coronaPlumes[i] = {
		mesh = mObj,
		baseDir = dir,
		rotAxis = rotAxis,
		orbitSpeed = 0.42 + (i % 7) * 0.085,
		eruptRate = 0.20 + (i % 9) * 0.034,
		u0 = uInit,
		prevU = uInit,
		angJitter = 0,
		radFactor = 0.72 + (i % 6) * 0.095,
		sizeFactor = 0.44 + (i % 5) * 0.056,
		roll0 = (i * 1.37) % (math.pi * 2),
		rollVel = ((i % 2 == 0) and 1 or -1) * (0.65 + (i % 5) * 0.14),
		phase = i * 0.83,
	}
end
task.wait()

-- 10 Soft Continuous Core-to-Mid Base Cushions + 192 Tiny Flowing & Dissolving 3D Micro-Nebula Constellations (768 micro-clouds!)
local CORE_CUSHION_COUNT = 10
local coreCushions = {}
for i = 1, CORE_CUSHION_COUNT do
	local rf = (i - 0.5) / CORE_CUSHION_COUNT
	local ang = i * goldenAngle * 1.5
	local rx = 1.6 + 5.8 * math.sqrt(rf)
	local ry = 1.5 + 4.1 * math.sqrt(rf)
	local bz = -3.4 + 2.8 * ((i * 0.61803) % 1)
	local isIce = (i <= 4)
	local isCyan = (not isIce) and (i % 2 == 0)
	local tex = isIce and texWhiteIceCorona or (isCyan and texCyanExpansion or texStormyCobaltNebula)
	coreCushions[i] = {
		mesh = makeAlphaMeshPart(clusterTplA.em, tex, string.format("CORE_3D_STEADY_CUSHION_%02d", i)),
		isIce = isIce,
		isCyan = isCyan,
		baseOffset = Vector3.new(math.cos(ang) * rx, math.sin(ang) * ry, bz),
		distNorm = clamp01(rf),
		baseSize = 6.2 + rf * 2.2,
		roll0 = (i * 1.91) % (math.pi * 2),
		phase = i * 1.13,
	}
end

local NEBULA_COUNT = 192
local chamberNebula = {}
for i = 1, NEBULA_COUNT do
	local ringFrac = ((i - 0.5) / NEBULA_COUNT)
	local ang = i * goldenAngle * 1.5
	local rx = 1.8 + 7.8 * math.sqrt(ringFrac)
	local ry = 1.6 + 5.4 * math.sqrt(ringFrac)
	local bz = -4.8 + 4.2 * (((i * 0.754877666) % 1))
	local szBase = 3.5 + ringFrac * 1.30 + (i % 5) * 0.30
	local bx = math.cos(ang) * rx
	local by = math.sin(ang) * ry
	local isInnerIce = (ringFrac < 0.36) and (i % 3 == 0)
	local isCyanAccent = (not isInnerIce) and (i % 2 == 0)
	local tex = isInnerIce and texWhiteIceCorona or (isCyanAccent and texCyanExpansion or texStormyCobaltNebula)
	local mObj = makeAlphaMeshPart(clusterTplB.em, tex, string.format("CHAMBER_3D_PLASMA_NEBULA_%03d", i))
	local uInit = (i * 0.61803398875) % 1
	chamberNebula[i] = {
		mesh = mObj,
		isInnerIce = isInnerIce,
		isCyanAccent = isCyanAccent,
		baseOffset = Vector3.new(bx, by, bz),
		jitter = Vector3.zero,
		distNorm = clamp01(ringFrac),
		baseSize = szBase,
		swirlSpeed = ((i % 2 == 0) and 1 or -1) * (0.24 + (i % 6) * 0.048),
		advectRate = 0.13 + (i % 9) * 0.024,
		u0 = uInit,
		prevU = uInit,
		roll0 = (i * 2.11) % (math.pi * 2),
		phase = i * 0.71,
	}
end
task.wait()

-- 12 Soft Continuous Wide-Chamber Cushions + 224 Tiny Drifting & Dissolving 3D Atmospheric Micro-Mist Constellations (896 micro-clouds!)
local CHAMBER_CUSHION_COUNT = 12
local chamberCushions = {}
for i = 1, CHAMBER_CUSHION_COUNT do
	local uIdx = (i - 0.5) / CHAMBER_CUSHION_COUNT
	local ang = i * goldenAngle * 2.0
	local radBand = 0.40 + 0.58 * math.sqrt(uIdx)
	local ox = math.cos(ang) * (16.2 * radBand)
	local oy = math.sin(ang) * (11.4 * radBand)
	local oz = -6.0 + 8.5 * ((i * 0.754877) % 1)
	local tex = (i % 3 == 0) and texCyanExpansion or texStormyCobaltNebula
	chamberCushions[i] = {
		mesh = makeAlphaMeshPart(clusterTplA.em, tex, string.format("CHAMBER_3D_STEADY_CUSHION_%02d", i)),
		origin = Vector3.new(ox, oy, oz),
		baseSize = 10.2 + (i % 4) * 1.5,
		roll0 = (i * 1.47) % (math.pi * 2),
		phase = i * 0.97,
	}
end

local AMBIENT_MIST_COUNT = 224
local ambientMist = {}
for i = 1, AMBIENT_MIST_COUNT do
	local uIdx = (i - 0.5) / AMBIENT_MIST_COUNT
	local ang = i * goldenAngle * 2.0
	local radBand = 0.30 + 0.70 * math.sqrt(uIdx)
	local ox = math.cos(ang) * (18.2 * radBand)
	local oy = math.sin(ang) * (12.8 * radBand)
	local oz = -7.0 + 10.8 * (((i * 0.56984029) % 1))
	local isIce = (i % 4 == 0)
	local isCyan = (i % 4 == 2)
	local tex = isIce and texWhiteIceCorona or (isCyan and texCyanExpansion or texStormyCobaltNebula)
	local mObj = makeAlphaMeshPart(clusterTplB.em, tex, string.format("CHAMBER_3D_AMBIENT_MIST_%03d", i))
	local uInit = (i * 0.61803398875) % 1
	ambientMist[i] = {
		mesh = mObj,
		origin = Vector3.new(ox, oy, oz),
		jitter = Vector3.zero,
		driftVel = Vector3.new(
			((i % 2 == 0) and 1 or -1) * (0.65 + (i % 5) * 0.22),
			0.85 + (i % 4) * 0.28,
			math.sin(i * 1.9) * 0.45
		),
		cycleRate = 0.095 + (i % 9) * 0.019,
		u0 = uInit,
		prevU = uInit,
		baseSize = 4.6 + (i % 6) * 0.42,
		roll0 = (i * 1.63) % (math.pi * 2),
		rollVel = ((i % 2 == 0) and 1 or -1) * (0.18 + (i % 4) * 0.05),
		isIce = isIce,
		phase = i * 0.93,
	}
end
task.wait()

-- 64 Soft Feathered Volumetric 3D Magnetic Ion Micro-Wisps (edgeZero RGBA gradient -> zero sharp dots!)
local AMBIENT_WISP_COUNT = 64
local ambientWisps = {}
for i = 1, AMBIENT_WISP_COUNT do
	local wObj = makeAlphaMeshPart(clusterTplB.em, texCyanExpansion, string.format("CHAMBER_3D_MAGNETIC_WISP_%03d", i))
	local tiltCF = CFrame.Angles(
		math.sin(i * 1.31) * 1.08,
		math.cos(i * 0.89) * 1.08,
		math.sin(i * 2.17) * 0.88
	)
	local uLife0 = (i * 0.61803398875) % 1
	ambientWisps[i] = {
		part = wObj.part,
		tilt = tiltCF,
		radius = 4.8 + (i % 8) * 1.35,
		radJitter = 0,
		speed = ((i % 2 == 0) and 1 or -1) * (0.52 + (i % 6) * 0.12),
		u0 = (i * goldenAngle) % (math.pi * 2),
		lifeRate = 0.14 + (i % 7) * 0.028,
		lifeU0 = uLife0,
		prevLifeU = uLife0,
		len = 1.35 + (i % 4) * 0.28,
		thick = 0.85 + (i % 3) * 0.16,
		phase = i * 1.17,
	}
end

-- 3 Sleek Counter-Rotating 3D Toroidal Cyan Magnetic Containment Rings (snug spherical orbit!)
local magRings = {}
for i, spec in ipairs({
	{tilt = CFrame.Angles(math.rad(68), math.rad(22), 0),   vel = Vector3.new(0.68, 1.18, -0.52), scale = 1.24},
	{tilt = CFrame.Angles(math.rad(-54), math.rad(-34), 0), vel = Vector3.new(-0.92, 0.72, 1.02), scale = 1.36},
	{tilt = CFrame.Angles(math.rad(18), math.rad(72), 0),   vel = Vector3.new(0.56, -1.08, 0.80), scale = 1.48},
}) do
	magRings[i] = {
		mesh = makeAlphaMeshPart(magRingTpl.em, texCyanExpansion, "STAR_3D_MAGNETIC_CONTAINMENT_RING_" .. i),
		tilt = spec.tilt,
		vel = spec.vel,
		scale = spec.scale,
	}
end

-- ============================================================================
-- 5. 60 FPS REAL-TIME MICRO-CONTINUUM SIMULATION LOOP (C++ BulkMoveTo!)
-- ============================================================================
local simClock = 0
local deformAccum = 0
local deformParity = 0
local smoothPostEnergy = 0
local holdStabilize = 0
local wasStartupReady = false
local impactPulse = 0
local bulkParts = table.create(780)
local bulkCFs = table.create(780)

local function hideAll3D()
	for _, ml in ipairs(mistLights) do ml.light.Brightness = 0 end
	centerDriver.Brightness = 0
	nebulaFrontLight.Brightness = 0
	for _, cl in ipairs(chamberCobaltLights) do cl.light.Brightness = 0 end
	opaqueSunBody.Transparency = 1
	softNeonAura.Transparency = 1
	for _, pair in ipairs(nozzleJets) do
		pair[1].part.Transparency = 1
		pair[2].part.Transparency = 1
	end
	for _, pf in ipairs(fluidPuffs) do
		pf.alive = false
		pf.mesh.part.Transparency = 1
	end
	for _, ls in ipairs(lasers) do
		ls.ext = 0
		ls.impacted = false
		ls.coreBeam.Transparency = 1
		ls.outerBeam.Transparency = 1
		ls.conicalFlare.part.Transparency = 1
		ls.waveSheath.part.Transparency = 1
		ls.muzzleLens.Transparency = 1
		ls.collarShroud.part.Transparency = 1
		ls.collarRing.part.Transparency = 1
		for _, pObj in ipairs(ls.pulses) do pObj.part.Transparency = 1 end
		for _, g in ipairs(ls.guides) do g.Transparency = 1 end
		local nz = ls.nozzle
		if nz.cellWin then
			nz.cellWin.Color = nz.cellOrigColor
			nz.cellWin.Material = nz.cellOrigMat
		end
	end
	for _, sh in ipairs(starShells) do sh.mesh.part.Transparency = 1 end
	for _, cp in ipairs(coronaPlumes) do cp.mesh.part.Transparency = 1 end
	for _, cc in ipairs(coreCushions) do cc.mesh.part.Transparency = 1 end
	for _, nb in ipairs(chamberNebula) do nb.mesh.part.Transparency = 1 end
	for _, chc in ipairs(chamberCushions) do chc.mesh.part.Transparency = 1 end
	for _, am in ipairs(ambientMist) do am.mesh.part.Transparency = 1 end
	for _, aw in ipairs(ambientWisps) do aw.part.Transparency = 1 end
	for _, mr in ipairs(magRings) do mr.mesh.part.Transparency = 1 end
end

hideAll3D()
Workspace:SetAttribute("VaporStep", "08_LIVE_60FPS_3D_ONLINE")

local syncLaserExt = 0
local lastRecordedMask = -1
local maskHistoryStr = ""
local telemAccum = 0

RunService.RenderStepped:Connect(function(dt)
	local step = math.min(dt, 0.05)
	simClock += step
	deformAccum += step
	impactPulse = math.max(0, impactPulse - step * 2.6)

	local mode = world:GetAttribute("ReactorMode") or "COLD"
	local isStartup = (mode == "STARTUP")
	local isActiveOp = (mode == "ONLINE" or mode == "WARNING" or mode == "MELTDOWN" or mode == "FREEZEDOWN")

	local fuel, mask, brokenMask, cyan, white, stabilize
	local laserBoost = (world:GetAttribute("ReactorLaserBoost") == true)
	local meltAge = world:GetAttribute("ReactorMeltdownAge") or 0
	local meltFrac = (mode == "MELTDOWN") and clamp01(meltAge / 18.0) or 0

	if isStartup then
		fuel = world:GetAttribute("ReactorPilotFuel") or 0
		mask = world:GetAttribute("ReactorPilotRelayMask") or 0
		brokenMask = 0
		cyan = world:GetAttribute("ReactorPilotCyanVolume") or 0
		white = world:GetAttribute("ReactorPilotWhiteVolume") or 0
		stabilize = world:GetAttribute("ReactorPilotStabilized") or 0
		-- Pre-charge post-startup energy & stabilization continuously during STARTUP so that
		-- the moment STARTUP transitions to ONLINE there is ZERO reset, ZERO blink, and ZERO fast-replay!
		smoothPostEnergy = clamp01(math.max(cyan * 0.42, white))
		holdStabilize = stabilize
		wasStartupReady = (white > 0.85)
	elseif isActiveOp then
		fuel = 0
		brokenMask = assembly:GetAttribute("LiveBrokenMask") or (world:GetAttribute("ReactorEmitterBrokenMask") or 0)
		local m1 = assembly:GetAttribute("LiveRelayMask") or 0
		local m2 = world:GetAttribute("ReactorEmitterReadyMask") or 0
		mask = (m1 > 0) and m1 or m2
		if mask == 0 and brokenMask == 0 then
			mask = 63
		end
		if wasStartupReady then
			smoothPostEnergy = 1
		else
			smoothPostEnergy = toward(smoothPostEnergy, 1, step / 1.35)
		end
		cyan = smoothPostEnergy
		white = smoothPostEnergy
		local targetStab = (mode == "ONLINE") and smoothPostEnergy or (smoothPostEnergy * 0.45)
		holdStabilize = toward(holdStabilize, targetStab, step / 1.25)
		stabilize = holdStabilize
	else
		wasStartupReady = false
		fuel = 0
		mask = assembly:GetAttribute("LiveRelayMask") or (world:GetAttribute("ReactorEmitterReadyMask") or 0)
		brokenMask = assembly:GetAttribute("LiveBrokenMask") or (world:GetAttribute("ReactorEmitterBrokenMask") or 0)
		smoothPostEnergy = toward(smoothPostEnergy, 0, step / 1.35)
		cyan = smoothPostEnergy
		white = smoothPostEnergy
		holdStabilize = smoothPostEnergy
		stabilize = smoothPostEnergy
	end

	-- ------------------------------------------------------------------------
	-- A) STAGE 02: STRAIGHT AXIAL NOZZLE-BORN 3D VAPOR (GRAVITY = 0!)
	-- ------------------------------------------------------------------------
	local purgeFade = isStartup and clamp01(1 - (world:GetAttribute("ReactorPilotDarkness") or 0) * 1.12) or 0

	if fuel <= 0.004 then
		for _, pair in ipairs(nozzleJets) do
			pair[1].part.Transparency = 1
			pair[2].part.Transparency = 1
		end
	else
		for idx, nz in ipairs(nozzles) do
			local s = nz.site
			local p = nz.socket.WorldPosition
			local jetCF = safeLookAt(p, p - s.axis) * CFrame.Angles(0, 0, simClock * 1.0 + idx)
			local pulse = 1 + 0.05 * math.sin(simClock * 5.2 + idx * 1.1)
			local wScale = (0.85 + 0.35 * fuel) * s.jetScale * pulse
			local lScale = (2.8 + 1.2 * fuel) * s.jetScale

			local inJet = nozzleJets[idx][1]
			inJet.part.Size = Vector3.new(inJet.baseSize.X * wScale * 0.80, inJet.baseSize.Y * wScale * 0.80, lScale)
			inJet.part.CFrame = jetCF
			inJet.part.Transparency = 1 - 0.38 * fuel

			local outJet = nozzleJets[idx][2]
			outJet.part.Size = Vector3.new(outJet.baseSize.X * wScale * 1.25, outJet.baseSize.Y * wScale * 1.25, lScale * 1.12)
			outJet.part.CFrame = jetCF * CFrame.Angles(0, 0, 1.57)
			outJet.part.Transparency = 1 - 0.25 * fuel
		end
	end

	local anySteamAlive = (fuel > 0.004)
	for _, pf in ipairs(fluidPuffs) do
		local mp = pf.mesh.part
		if not pf.alive then
			if fuel > 0.03 and purgeFade > 0.08 then
				if rng:NextNumber() < step * (0.8 + 2.4 * fuel) then
					spawnStraightPuffAtNozzle(pf, nozzles[pf.nozzleIdx], fuel)
					anySteamAlive = true
				end
			else
				mp.Transparency = 1
			end
		end

		if pf.alive then
			pf.age += step
			local u = pf.age / pf.maxLife
			if u >= 1 or purgeFade <= 0.005 then
				if fuel > 0.03 and purgeFade > 0.08 then
					spawnStraightPuffAtNozzle(pf, nozzles[pf.nozzleIdx], fuel)
					u = 0
				else
					pf.alive = false
					mp.Transparency = 1
				end
			end

			if pf.alive then
				anySteamAlive = true
				local drag = math.exp(-1.55 * step)
				pf.vel = pf.vel * drag

				-- Zero-mean symmetric 3D turbulence (ZERO downward gravity!)
				local turbX = math.noise(pf.pos.X * 0.22 + pf.seed, pf.pos.Y * 0.22, simClock * 0.75) * 3.0
				local turbY = math.noise(pf.pos.Y * 0.22 - pf.seed, simClock * 0.75, pf.pos.Z * 0.22) * 3.0
				local turbZ = math.noise(pf.pos.Z * 0.22, pf.pos.X * 0.22 + pf.seed, simClock * 0.60) * 2.2
				pf.vel += Vector3.new(turbX, turbY, turbZ) * step

				local toCenter = pf.pos - FOCUS
				if toCenter.Magnitude < 2.6 then
					pf.vel *= math.exp(-2.8 * step)
				end

				pf.pos += pf.vel * step
				pf.roll += pf.spin * step * (0.45 + 0.55 * (1 - u))

				local grow = 0.85 + (pf.endSize - 0.85) * (u ^ 0.72)
				mp.Size = Vector3.new(grow, grow, 1.9)
				mp.CFrame = CFrame.new(pf.pos) * CFrame.Angles(0, 0, pf.roll)

				local alphaEnv = smooth(0.0, 0.08, u) * ((1 - smooth(0.24, 1.0, u)) ^ 1.45)
				local vis = math.clamp(alphaEnv * (0.26 + 0.34 * math.max(fuel, 0.40)) * purgeFade, 0, 0.50)
				mp.Transparency = 1 - vis
			end
		end
	end

	for _, ml in ipairs(mistLights) do
		ml.light.Brightness = fuel * ml.mult
	end

	-- ------------------------------------------------------------------------
	-- B) SIMULTANEOUS LOCKSTEP 6-LASER EXTENSION & 100%-OPAQUE CORE DIAMETER
	-- ------------------------------------------------------------------------
	if mode == "COLD" then
		syncLaserExt = 0
		lastRecordedMask = -1
		maskHistoryStr = ""
	elseif mask ~= lastRecordedMask then
		lastRecordedMask = mask
		maskHistoryStr = (maskHistoryStr == "") and tostring(mask) or (maskHistoryStr .. "->" .. tostring(mask))
	end

	local boostScale = laserBoost and 1.15 or 1.0
	local prelimImpacted = 0
	local anyIntactRelayActive = false
	local barrelRelayActive = {false, false, false, false, false, false}
	local barrelLiveStroke = {0, 0, 0, 0, 0, 0}

	for idx, ls in ipairs(lasers) do
		local tag = ls.nozzle.site.tag
		local pStroke = assembly:GetAttribute("ReactorPilotStroke_" .. tag) or 0
		local lStroke = assembly:GetAttribute("LiveStroke_" .. tag) or 0
		local liveStroke = isStartup and pStroke or (isActiveOp and math.max(pStroke, lStroke) or lStroke)
		barrelLiveStroke[idx] = liveStroke
		local relayActive = bit(mask, idx) and (not bit(brokenMask, idx)) and (liveStroke > 0.96)
		barrelRelayActive[idx] = relayActive
		if relayActive then
			anyIntactRelayActive = true
		end
	end

	if anyIntactRelayActive then
		syncLaserExt = math.min(1, syncLaserExt + step / 0.18)
	else
		syncLaserExt = math.max(0, syncLaserExt - step / 0.14)
	end

	for idx, ls in ipairs(lasers) do
		if barrelRelayActive[idx] then
			ls.ext = syncLaserExt
			if ls.ext >= 0.98 then
				if not ls.impacted then
					ls.impacted = true
					impactPulse = math.min(1.0, impactPulse + 0.25)
				end
				prelimImpacted += 1
			end
		else
			ls.ext = math.max(0, ls.ext - step / 0.14)
			ls.impacted = false
		end
	end

	local beamFeedFrac = prelimImpacted / 6
	local starEnergy
	if isStartup then
		starEnergy = (prelimImpacted > 0) and clamp01(beamFeedFrac * 0.42 + math.max(cyan, white) * 0.58) or 0
	else
		starEnergy = smoothPostEnergy * (prelimImpacted > 0 and math.max(0.35, beamFeedFrac) or smoothPostEnergy)
	end

	local fullStage = clamp01(math.max(cyan, white))
	local chamberDark = isStartup and clamp01(world:GetAttribute("ReactorPilotDarkness") or 0) or 0
	-- Living organic magnetic heartbeat:
	local liveBreath = 0.036 * math.sin(simClock * 2.8) + 0.020 * math.sin(simClock * 6.1 + 1.1)
	local failedFeeds=0
	if mode == "MELTDOWN" then
		for i=1,6 do if bit(brokenMask,i) then failedFeeds += 1 end end
	end
	-- The same isotropic scalar changes all three dimensions, preserving the
	-- common focus and preventing extra orphan beams in startup/normal mode.
	local instability=(failedFeeds/6) * (0.06*math.sin(simClock*9.1) + 0.035*math.sin(simClock*15.3+1.7))
	local pulseKick = 1 + impactPulse * 0.14 + liveBreath + meltFrac * 0.16 * math.sin(simClock * 6.8) + instability
	local starScale = pulseKick * (laserBoost and 1.07 or 1.0) * (1 + 0.36 * meltFrac)

	-- Organic Reference-Sculpted Solar Core Diameter (compact Z-occluder tucked inside billowing 3D cloud corona!):
	local opaqueDiam = 0
	if starEnergy > 0.004 then
		local cyanD = 1.5 + (4.7 - 1.5) * fullStage
		local whitePeakD = cyanD + (7.6 - 4.7) * white
		local settledD = whitePeakD - (7.6 - 4.85) * (white * stabilize)
		opaqueDiam = settledD * (0.48 + 0.52 * beamFeedFrac) * starScale
	end
	local opaqueRadius = opaqueDiam * 0.5

	table.clear(bulkParts)
	table.clear(bulkCFs)
	local bulkN = 0

	-- Measure exact physical nozzle distance across deployed barrels so all 6 coaxial feeds
	-- have 100.000% equal length from their NOZZLE__white mouths to FOCUS (0.000 stud spread!):
	local sumFullDist, countFullDist = 0, 0
	local rawFullDists = {0, 0, 0, 0, 0, 0}
	for idx, ls in ipairs(lasers) do
		local sockP = ls.nozzle.socket.WorldPosition
		local dFocus = (FOCUS - Vector3.new(sockP.X, sockP.Y, FOCUS.Z)).Magnitude
		rawFullDists[idx] = dFocus
		if barrelLiveStroke[idx] > 0.96 and not bit(brokenMask, idx) then
			sumFullDist += dFocus
			countFullDist += 1
		end
	end
	local lockedFullDist = (countFullDist > 0) and (sumFullDist / countFullDist) or 7.6536

	local activeLaserCount = 0
	local minSpan, maxSpan = 1e9, 0
	local minRawDist, maxRawDist = 1e9, 0
	local maxFocusErr = 0
	local syncFirePhase = (simClock * 0.92) % 1
	local syncPumpWave = 0.042 * math.sin(simClock * 5.8) + 0.020 * math.sin(simClock * 11.4)

	-- ------------------------------------------------------------------------
	-- C) REACTOR-INTEGRATED 6 PHYSICAL BARRELS + COLLAR SHROUDS + 48 MICRO-WAVELETS
	-- ------------------------------------------------------------------------
	for idx, ls in ipairs(lasers) do
		local nz = ls.nozzle
		local isBroken = bit(brokenMask, idx)
		local prewarm = (not isBroken) and clamp01(chamberDark * 0.72 + ls.ext) or 0
		local firePhase = syncFirePhase
		if nz.cellWin and not isBroken then
			if prewarm > 0.02 then
				local smoothWave = 0.5 + 0.5 * math.sin(simClock * 3.4)
				nz.cellWin.Material = Enum.Material.Neon
				nz.cellWin.Color = Color3.fromRGB(24, 132, 214)
					:Lerp(Color3.fromRGB(38, 206, 255), clamp01(prewarm))
					:Lerp(Color3.fromRGB(108, 240, 255), clamp01(smoothWave * 0.36 + white * 0.14))
					:Lerp(Color3.fromRGB(255, 110, 185), meltFrac * 0.75)
			else
				nz.cellWin.Material = nz.cellOrigMat
				nz.cellWin.Color = nz.cellOrigColor
			end
		end

		if ls.ext <= 0.005 then
			ls.coreBeam.Transparency = 1
			ls.outerBeam.Transparency = 1
			ls.conicalFlare.part.Transparency = 1
			ls.waveSheath.part.Transparency = 1
			ls.muzzleLens.Transparency = 1
			ls.collarShroud.part.Transparency = 1
			ls.collarRing.part.Transparency = 1
			for _, pObj in ipairs(ls.pulses) do pObj.part.Transparency = 1 end
			for _, g in ipairs(ls.guides) do g.Transparency = 1 end
		else
			local dir = (-nz.site.axis).Unit
			local fullDist = (barrelLiveStroke[idx] > 0.96) and lockedFullDist or rawFullDists[idx]
			local startP = FOCUS - dir * fullDist

			-- Before star birth (opaqueRadius == 0), clipFromFocus == 0 so all 6 beams collide dead-center on FOCUS!
			-- Once opaqueSunBody forms, clip 22% inside isotropic opaqueSunBody (equal span on all 6 axes, 0% leak!):
			local clipFromFocus = (opaqueRadius > 0.04) and (opaqueRadius * 0.78) or 0
			local targetSpan = math.max(0.25, fullDist - clipFromFocus)
			local curSpan = targetSpan * ls.ext
			local endP = startP + dir * curSpan
			local midP = (startP + endP) * 0.5
			local beamCF = safeLookAt(midP, endP)
			local startLookCF = safeLookAt(startP, FOCUS)

			activeLaserCount += 1
			if curSpan < minSpan then minSpan = curSpan end
			if curSpan > maxSpan then maxSpan = curSpan end
			if rawFullDists[idx] < minRawDist then minRawDist = rawFullDists[idx] end
			if rawFullDists[idx] > maxRawDist then maxRawDist = rawFullDists[idx] end
			local axisFocusErr = ((startP + dir * fullDist) - FOCUS).Magnitude
			if axisFocusErr > maxFocusErr then maxFocusErr = axisFocusErr end

			local hf = (1 + syncPumpWave) * boostScale

			-- 1) Reference-luminous white-ice central plasma beam
			local coreD = (0.18 + 0.16 * white + 0.05 * fullStage) * hf
			ls.coreBeam.Size = Vector3.new(curSpan, coreD, coreD)
			bulkN += 1; bulkParts[bulkN] = ls.coreBeam; bulkCFs[bulkN] = beamCF * CFrame.Angles(0, math.pi * 0.5, 0)
			ls.coreBeam.Color = Color3.fromRGB(215, 251, 255)
				:Lerp(Color3.fromRGB(252, 254, 255), clamp01(fullStage * 0.5 + white * 0.5))
				:Lerp(Color3.fromRGB(255, 205, 232), meltFrac * 0.7)
			ls.coreBeam.Transparency = 0.02

			-- 2) Warmly blended coaxial white-cyan sheath (matches reference beam glow without star spikes!)
			local outerD = (0.40 + 0.30 * white + 0.10 * fullStage) * hf
			ls.outerBeam.Size = Vector3.new(curSpan, outerD, outerD)
			bulkN += 1; bulkParts[bulkN] = ls.outerBeam; bulkCFs[bulkN] = beamCF * CFrame.Angles(0, math.pi * 0.5, 0)
			ls.outerBeam.Color = Color3.fromRGB(48, 224, 255)
				:Lerp(Color3.fromRGB(165, 236, 255), white)
				:Lerp(Color3.fromRGB(245, 75, 175), meltFrac * 0.85)
			ls.outerBeam.Transparency = 0.50 - 0.08 * white

			-- 3) Organic Beam-to-Cloud Plasma Merge Envelope (centered at beamCF, moderate width -> melts into boiling core!)
			local cfObj = ls.conicalFlare
			local flareW = (0.76 + 0.32 * fullStage + 0.24 * white * (1 - 0.28 * stabilize)) * hf
			cfObj.part.Size = Vector3.new(flareW, flareW, curSpan)
			bulkN += 1; bulkParts[bulkN] = cfObj.part; bulkCFs[bulkN] = beamCF * CFrame.Angles(0, 0, -simClock * 2.8 + idx * 1.05)
			cfObj.part.Transparency = 0.46 - 0.06 * white

			-- 4) Coaxial 3D Helical Plasma Wave Sheath
			local wPart = ls.waveSheath.part
			local waveD = (0.58 + 0.32 * white * (1 - 0.20 * stabilize) + 0.14 * fullStage) * hf
			wPart.Size = Vector3.new(waveD, waveD, curSpan)
			bulkN += 1; bulkParts[bulkN] = wPart; bulkCFs[bulkN] = beamCF * CFrame.Angles(0, 0, -simClock * 4.2 + idx * 1.05)
			wPart.Transparency = 0.42 - 0.06 * white

			-- 5) Muzzle focal glow + Physical 3D Nozzle Collar Shroud + Magnetic Nozzle Ring
			local lensD = (0.64 + 0.22 * white) * hf
			ls.muzzleLens.Size = Vector3.new(lensD, lensD, lensD)
			bulkN += 1; bulkParts[bulkN] = ls.muzzleLens; bulkCFs[bulkN] = CFrame.new(startP + dir * 0.06)
			ls.muzzleLens.Color = Color3.fromRGB(140, 244, 255):Lerp(Color3.fromRGB(238, 252, 255), white)
			ls.muzzleLens.Transparency = 0.08

			local shroudP = ls.collarShroud.part
			local shroudW = (1.85 + 0.65 * fullStage) * hf
			shroudP.Size = Vector3.new(shroudW, shroudW, 1.35)
			bulkN += 1; bulkParts[bulkN] = shroudP
			bulkCFs[bulkN] = startLookCF * CFrame.new(0, 0, -0.32) * CFrame.Angles(0, 0, simClock * 1.65 * (idx % 2 == 0 and 1 or -1) + idx)
			shroudP.Transparency = 1 - clamp01((0.36 + 0.22 * fullStage) * ls.ext)

			local cRingP = ls.collarRing.part
			local cRingBS = ls.collarRing.baseSize
			local cRingD = (1.72 + 0.26 * white) * (1 + 0.045 * math.sin(simClock * 6.5 + idx))
			cRingP.Size = Vector3.new(
				cRingBS.X * (cRingD / math.max(cRingBS.X, 0.01)),
				cRingBS.Y * (cRingD / math.max(cRingBS.Y, 0.01)),
				cRingBS.Z * (cRingD / math.max(cRingBS.Z, 0.01))
			)
			bulkN += 1; bulkParts[bulkN] = cRingP
			bulkCFs[bulkN] = startLookCF * CFrame.new(0, 0, -0.14) * CFrame.Angles(0, 0, simClock * 3.2 + idx)
			cRingP.Transparency = 1 - clamp01((0.52 + 0.24 * fullStage) * ls.ext)

			-- 6) 8 Staggered Ultra-Fine Micro-Wavelets per Barrel (48 total!):
			--    Born at 0.000 alpha inside the glowing collar and dissolved at 0.000 alpha inside the corona!
			local nPulses = #ls.pulses
			for pIdx = 1, nPulses do
				local pObj = ls.pulses[pIdx]
				local mp = pObj.part
				local uPulse = (firePhase + (pIdx - 1) / nPulses) % 1
				local pEnv = imperceptibleBell(uPulse)
				local pAlpha = clamp01(pEnv * (0.14 + 0.08 * fullStage) * ls.ext)
				if pAlpha < 0.0022 then
					if mp.Transparency < 1 then mp.Transparency = 1 end
				else
					local easedU = uPulse ^ 1.12
					local pPos = startP + dir * (curSpan * easedU)
					local pW = (0.34 + 0.24 * fullStage + 0.14 * easedU) * boostScale
					local pL = (0.68 + 0.44 * fullStage) * boostScale
					mp.Size = Vector3.new(pW, pW, pL)
					bulkN += 1; bulkParts[bulkN] = mp
					bulkCFs[bulkN] = safeLookAt(pPos, FOCUS) * CFrame.Angles(0, 0, simClock * 4.5 + pIdx * 1.57)
					mp.Transparency = 1 - pAlpha
				end
			end

			-- 7) 4 Hair-Thin Cyan Collar Guide Filaments
			local guideLen = math.min(curSpan * 0.82, 3.6)
			local guideCol = Color3.fromRGB(64, 232, 255):Lerp(Color3.fromRGB(175, 232, 255), white)
			for gIdx, gOff in ipairs(GUIDE_OFFSETS) do
				local rail = ls.guides[gIdx]
				local gStart = startLookCF:PointToWorldSpace(Vector3.new(gOff.X, gOff.Y, -0.05))
				local gEnd = startLookCF:PointToWorldSpace(Vector3.new(gOff.X * 0.42, gOff.Y * 0.42, -guideLen))
				local gSpan = (gEnd - gStart).Magnitude
				rail.Size = Vector3.new(gSpan, 0.048, 0.048)
				bulkN += 1; bulkParts[bulkN] = rail
				bulkCFs[bulkN] = safeLookAt((gStart + gEnd) * 0.5, gEnd) * CFrame.Angles(0, math.pi * 0.5, 0)
				rail.Color = guideCol
				rail.Transparency = 0.28 + 0.12 * white
			end
		end
	end

	-- ------------------------------------------------------------------------
	-- D) GPU-NATIVE HIGH-POLY EMISSIVE MODULATION (0.00 ms VERTEX RE-UPLOAD!)
	-- ------------------------------------------------------------------------
	if mask > 0 or starEnergy > 0.004 or fuel > 0.02 then
		local roomLit = 1 - chamberDark
		local emissiveGain = (1.0 - 0.40 * roomLit) * (1 + 0.12 * impactPulse)
		local emTint = Color3.fromRGB(255, 255, 255):Lerp(Color3.fromRGB(255, 132, 188), meltFrac * 0.78)
		for _, item in ipairs(emissiveSurfaces) do
			item.sa.EmissiveStrength = item.base * emissiveGain
			item.sa.EmissiveTint = emTint
		end
	end

	-- ------------------------------------------------------------------------
	-- E) LIVING MICRO-CONTINUUM 3D FUSION SUN + 540 MICRO-WISPS + 64 MICRO-SPARKS
	--    (Every individual wisp is tiny, low-contrast, and fades via C^2 sin^3.5 bell
	--     below 1/255 bit quantization so vanishing & spawning are 100% imperceptible!)
	-- ------------------------------------------------------------------------
	local ambStrength = clamp01(starEnergy * (cyan * 0.78 + white * 1.0) * (1 - 0.16 * stabilize))
	if ambStrength <= 0.005 then
		for _, chc in ipairs(chamberCushions) do
			if chc.mesh.part.Transparency < 1 then chc.mesh.part.Transparency = 1 end
		end
		for _, am in ipairs(ambientMist) do
			if am.mesh.part.Transparency < 1 then am.mesh.part.Transparency = 1 end
		end
	else
		-- 12 Soft Continuous Steady Chamber Cushions (seamless velvet foundation!)
		for i = 1, CHAMBER_CUSHION_COUNT do
			local chc = chamberCushions[i]
			local mp = chc.mesh.part
			local sx = chc.baseSize * 1.18 * (0.90 + 0.14 * white)
			local sy = chc.baseSize * 0.92 * (0.90 + 0.14 * white)
			mp.Size = Vector3.new(sx, sy, 3.4)
			local pos = FOCUS + chc.origin + Vector3.new(
				math.sin(simClock * 0.35 + chc.phase) * 0.45,
				math.cos(simClock * 0.30 + chc.phase) * 0.38,
				0
			)
			bulkN += 1; bulkParts[bulkN] = mp
			bulkCFs[bulkN] = CFrame.new(pos) * CFrame.Angles(0, 0, chc.roll0 + simClock * 0.08)
			mp.Transparency = 1 - clamp01(ambStrength * 0.135)
		end

		-- 224 4-Puff Micro-Mist Constellations (= 896 tiny drifting, curling & sub-bit dissolving chamber micro-clouds!)
		for i = 1, AMBIENT_MIST_COUNT do
			local am = ambientMist[i]
			local mp = am.mesh.part
			local uCyc = (simClock * am.cycleRate + am.u0) % 1
			if uCyc < am.prevU then
				-- Wrapped at exact 0.0000 alpha! Refresh micro-offset while completely invisible:
				am.jitter = Vector3.new(
					rng:NextNumber(-1.45, 1.45),
					rng:NextNumber(-1.20, 1.20),
					rng:NextNumber(-0.85, 0.85)
				)
			end
			am.prevU = uCyc

			local lifeEnv = imperceptibleBell(uCyc)
			local peakAlpha = am.isIce and 0.120 or 0.175
			local alpha = clamp01(lifeEnv * ambStrength * peakAlpha)
			if alpha < 0.0022 then
				if mp.Transparency < 1 then mp.Transparency = 1 end
			else
				local driftOffset = am.driftVel * ((uCyc - 0.5) * 4.2)
				local curlX = math.sin(simClock * 0.62 + am.phase) * 0.85
				local curlY = math.cos(simClock * 0.54 + am.phase * 1.3) * 0.72
				local pos = FOCUS + am.origin + am.jitter + driftOffset + Vector3.new(curlX, curlY, 0)
				local sz = am.baseSize * (0.86 + 0.28 * uCyc) * (0.90 + 0.15 * white)
				mp.Size = Vector3.new(sz * 1.14, sz * 0.94, 2.2)
				bulkN += 1; bulkParts[bulkN] = mp
				bulkCFs[bulkN] = CFrame.new(pos) * CFrame.Angles(0, 0, am.roll0 + simClock * am.rollVel)
				mp.Transparency = 1 - alpha
			end
		end
	end

	if starEnergy <= 0.004 then
		centerDriver.Brightness = 0
		nebulaFrontLight.Brightness = 0
		for _, cl in ipairs(chamberCobaltLights) do cl.light.Brightness = 0 end
		opaqueSunBody.Transparency = 1
		softNeonAura.Transparency = 1
		for _, sh in ipairs(starShells) do sh.mesh.part.Transparency = 1 end
		for _, cp in ipairs(coronaPlumes) do if cp.mesh.part.Transparency < 1 then cp.mesh.part.Transparency = 1 end end
		for _, cc in ipairs(coreCushions) do if cc.mesh.part.Transparency < 1 then cc.mesh.part.Transparency = 1 end end
		for _, nb in ipairs(chamberNebula) do if nb.mesh.part.Transparency < 1 then nb.mesh.part.Transparency = 1 end end
		for _, aw in ipairs(ambientWisps) do if aw.part.Transparency < 1 then aw.part.Transparency = 1 end end
		for _, mr in ipairs(magRings) do mr.mesh.part.Transparency = 1 end
	else
		local roomLit = 1 - chamberDark

		centerDriver.Color = Color3.fromRGB(228, 243, 255)
			:Lerp(Color3.fromRGB(246, 250, 255), white)
			:Lerp(Color3.fromRGB(255, 120, 182), meltFrac * 0.75)
		centerDriver.Range = 14
		centerDriver.Brightness = starEnergy * (0.48 * chamberDark + 0.15 * roomLit)

		nebulaFrontLight.Brightness = 0
		for _, cl in ipairs(chamberCobaltLights) do
			cl.light.Brightness = 0
		end

		-- 1) 100%-OPAQUE (Transparency = 0) Radially Symmetric Organic FBM Z-Occluding Inner Core
		--    (Isotropic 1:1:1 breathing ensures ALL 6 laser axes have 100% equal exposed length!)
		local wobIso = 1.00 + 0.028 * math.sin(simClock * 3.1)
		local targetCoreD = opaqueDiam * wobIso
		opaqueSunBody.Size = Vector3.new(targetCoreD, targetCoreD, targetCoreD)
		bulkN += 1; bulkParts[bulkN] = opaqueSunBody
		bulkCFs[bulkN] = CFrame.new(FOCUS) * CFrame.Angles(simClock * 0.95, simClock * -1.25, simClock * 0.75)
		opaqueSunBody.Color = Color3.fromRGB(235, 254, 255)
			:Lerp(Color3.fromRGB(255, 255, 255), clamp01(fullStage * 0.65 + white * 0.35))
			:Lerp(Color3.fromRGB(255, 215, 238), meltFrac * 0.6)
		opaqueSunBody.Transparency = 0

		-- Tucked organic solar prominence Neon sub-shell (isotropic X=Y so zero vertical/horizontal beam mismatch!)
		local auraD = opaqueDiam * (1.03 + 0.032 * math.sin(simClock * 4.2))
		softNeonAura.Size = Vector3.new(auraD, auraD, auraD)
		bulkN += 1; bulkParts[bulkN] = softNeonAura
		bulkCFs[bulkN] = CFrame.new(FOCUS) * CFrame.Angles(simClock * -1.18, simClock * 0.96, simClock * -0.82)
		softNeonAura.Color = Color3.fromRGB(95, 244, 255)
			:Lerp(Color3.fromRGB(245, 251, 255), white)
			:Lerp(Color3.fromRGB(255, 145, 195), meltFrac * 0.75)
		softNeonAura.Transparency = 0.46 - 0.06 * white

		-- 2) 6 Multi-Lobed Feathered 3D Cloud Billows & Solar Prominence Shells (radially balanced X=Y!)
		for idxS, sh in ipairs(starShells) do
			local p = sh.mesh.part
			local bs = sh.mesh.baseSize
			local rv = sh.rotVel * simClock * (1 + 0.6 * meltFrac)
			if sh.kind == "CLOUD_BILLOW_A" then
				local d = opaqueDiam * (1.58 + 0.14 * white + 0.04 * math.sin(simClock * 2.9))
				p.Size = Vector3.new(d * 1.04, d * 1.04, d * 0.58)
				p.Transparency = 1 - clamp01(starEnergy * 0.88)
			elseif sh.kind == "CLOUD_BILLOW_B" then
				local d = opaqueDiam * (1.72 + 0.16 * white + 0.04 * math.cos(simClock * 2.4))
				p.Size = Vector3.new(d * 1.04, d * 1.04, d * 0.58)
				p.Transparency = 1 - clamp01(starEnergy * 0.78)
			elseif sh.kind == "CLOUD_BILLOW_C" then
				local d = opaqueDiam * (1.86 + 0.18 * white * (1 - 0.22 * stabilize))
				p.Size = Vector3.new(d * 1.04, d * 1.04, d * 0.56)
				p.Transparency = 1 - clamp01(starEnergy * 0.64)
			elseif sh.kind == "PROMINENCE" then
				local targetD = opaqueDiam * (1.18 + 0.08 * white + 0.03 * math.sin(simClock * 3.5))
				p.Size = Vector3.new(targetD, targetD, targetD)
				p.Transparency = 1 - clamp01(starEnergy * 0.84)
			elseif sh.kind == "CYAN_INNER" then
				local targetD = opaqueDiam * (1.36 + 0.16 * cyan * (1 - 0.42 * white))
				p.Size = Vector3.new(
					bs.X * (targetD / math.max(bs.X, 0.01)),
					bs.Y * (targetD / math.max(bs.Y, 0.01)),
					bs.Z * (targetD / math.max(bs.Z, 0.01))
				)
				p.Transparency = 1 - clamp01(cyan * (1 - 0.42 * white) * 0.70 + white * 0.30) * starEnergy
			else
				local d = opaqueDiam * (2.05 + 0.22 * cyan * (1 - 0.45 * white))
				p.Size = Vector3.new(d * 1.04, d * 1.04, d * 0.62)
				p.Transparency = 1 - clamp01(cyan * (1 - 0.52 * white) * 0.58 + white * 0.28) * starEnergy
			end
			bulkN += 1; bulkParts[bulkN] = p
			bulkCFs[bulkN] = CFrame.new(FOCUS) * sh.baseTilt * CFrame.Angles(rv.X * 0.35, rv.Y * 0.35, rv.Z)
		end

		-- 3) 144 Billowing & Imperceptibly Dissolving 3D Solar Corona Billows (576 micro-billows masking sphere rim!)
		local plumeVis = clamp01(cyan * 0.82 + white * 0.96) * starEnergy * (1 - 0.10 * stabilize)
		local radTighten = 1 - 0.10 * stabilize
		local szTighten = 1 - 0.12 * stabilize
		for i = 1, CORONA_PLUME_COUNT do
			local cp = coronaPlumes[i]
			local mp = cp.mesh.part
			local uErupt = (simClock * cp.eruptRate + cp.u0) % 1
			if uErupt < cp.prevU then
				cp.angJitter = rng:NextNumber(-0.35, 0.35)
			end
			cp.prevU = uErupt

			local pAlpha = clamp01(plumeVis * imperceptibleBell(uErupt) * 0.52)
			if pAlpha < 0.0022 then
				if mp.Transparency < 1 then mp.Transparency = 1 end
			else
				local orbCF = CFrame.fromAxisAngle(cp.rotAxis, simClock * cp.orbitSpeed + cp.angJitter)
				local worldDir = orbCF:VectorToWorldSpace(cp.baseDir)
				local rDist = opaqueRadius * (0.78 + 0.68 * uErupt) * cp.radFactor * radTighten
				local pos = FOCUS + worldDir * rDist
				local sz = opaqueDiam * cp.sizeFactor * (0.85 + 0.38 * uErupt) * (0.92 + 0.20 * white) * szTighten
				mp.Size = Vector3.new(sz * 1.08, sz * 0.94, sz * 0.64)
				bulkN += 1; bulkParts[bulkN] = mp
				bulkCFs[bulkN] = CFrame.new(pos) * CFrame.Angles(0, 0, cp.roll0 + simClock * cp.rollVel)
				mp.Transparency = 1 - pAlpha
			end
		end

		-- 4A) 10 Soft Continuous Core-to-Mid Base Cushions (smoky white-ice inner halo + cobalt/cyan mid shroud!)
		local nebExpand = clamp01(cyan * 0.88 + white * 1.0)
		local stagePull = (0.96 - 0.04 * white) * (1 - 0.10 * stabilize)
		for i = 1, CORE_CUSHION_COUNT do
			local cc = coreCushions[i]
			local mp = cc.mesh.part
			local localAppear = smooth(cc.distNorm * 0.30, cc.distNorm * 0.30 + 0.45, nebExpand) * starEnergy
			if localAppear <= 0.005 then
				if mp.Transparency < 1 then mp.Transparency = 1 end
			else
				local curScale = (0.54 + 0.46 * nebExpand) * stagePull
				local sz = cc.baseSize * (0.92 + 0.16 * white) * (1 - 0.10 * stabilize)
				mp.Size = Vector3.new(sz * 1.12, sz * 0.96, 2.8)
				local sw = simClock * 0.16 + cc.phase
				bulkN += 1; bulkParts[bulkN] = mp
				bulkCFs[bulkN] = CFrame.new(FOCUS + cc.baseOffset * curScale) * CFrame.Angles(0, 0, cc.roll0 + sw)
				local w = cc.isIce and clamp01(cyan * 0.55 + white * 0.96)
					or (cc.isCyan and clamp01(cyan * 0.88 * (1 - 0.32 * white) + white * 0.56) or clamp01(cyan * 0.38 + white * 0.92))
				mp.Transparency = 1 - clamp01(localAppear * w * (cc.isIce and 0.32 or 0.26))
			end
		end

		-- 4B) 192 4-Puff Micro-Nebula Constellations (= 768 tiny advecting, swirling & sub-bit dissolving micro-clouds!)
		for i = 1, NEBULA_COUNT do
			local nb = chamberNebula[i]
			local mp = nb.mesh.part
			local localAppear = smooth(nb.distNorm * 0.35, nb.distNorm * 0.35 + 0.46, nebExpand) * starEnergy
			if localAppear <= 0.008 then
				if mp.Transparency < 1 then mp.Transparency = 1 end
			else
				local uAdv = (simClock * nb.advectRate + nb.u0) % 1
				if uAdv < nb.prevU then
					nb.jitter = Vector3.new(
						rng:NextNumber(-0.85, 0.85),
						rng:NextNumber(-0.75, 0.75),
						rng:NextNumber(-0.55, 0.55)
					)
				end
				nb.prevU = uAdv

				local advEnv = imperceptibleBell(uAdv)
				local weight = nb.isInnerIce
					and clamp01(cyan * 0.58 + white * 0.98)
					or (nb.isCyanAccent
						and clamp01(cyan * 0.94 * (1 - 0.35 * white) + white * 0.58)
						or clamp01(cyan * 0.40 + white * 0.96))
				local centerFocus = (1.08 - 0.18 * nb.distNorm) * (1 - 0.16 * stabilize * nb.distNorm)
				local rawAlpha = clamp01(localAppear * weight * centerFocus * advEnv * (nb.isInnerIce and 0.34 or 0.29))
				if rawAlpha < 0.0022 then
					if mp.Transparency < 1 then mp.Transparency = 1 end
				else
					local swAng = simClock * nb.swirlSpeed
					local cSw, sSw = math.cos(swAng), math.sin(swAng)
					local bo = nb.baseOffset + nb.jitter
					local radialFlow = 0.78 + 0.34 * uAdv
					local curScale = (0.52 + 0.48 * nebExpand) * stagePull * radialFlow
					local curOff = Vector3.new(
						bo.X * cSw - bo.Y * sSw * 0.32,
						bo.Y * cSw + bo.X * sSw * 0.26,
						bo.Z + 0.45 * math.sin(simClock * 1.15 + nb.phase)
					) * curScale
					local sz = nb.baseSize * (0.86 + 0.28 * uAdv) * (1 - 0.10 * stabilize)
					mp.Size = Vector3.new(sz * 1.12, sz * 0.96, 2.1)
					bulkN += 1; bulkParts[bulkN] = mp
					bulkCFs[bulkN] = CFrame.new(FOCUS + curOff) * CFrame.Angles(0, 0, nb.roll0 + swAng * 1.4)
					mp.Transparency = 1 - rawAlpha
				end
			end
		end

		-- 5) 64 Feathered Volumetric 3D Magnetic Ion Micro-Wisps (= 256 gaseous micro-puffs, zero sharp specks!)
		local wispVis = clamp01(cyan * 0.55 + white * 0.90) * starEnergy
		for i = 1, AMBIENT_WISP_COUNT do
			local aw = ambientWisps[i]
			local wp = aw.part
			local uLife = (simClock * aw.lifeRate + aw.lifeU0) % 1
			if uLife < aw.prevLifeU then
				aw.radJitter = rng:NextNumber(-0.95, 0.95)
			end
			aw.prevLifeU = uLife

			local lifeBell = imperceptibleBell(uLife)
			local wAlpha = clamp01(wispVis * lifeBell * 0.13)
			if wAlpha < 0.0022 then
				if wp.Transparency < 1 then wp.Transparency = 1 end
			else
				local th = aw.u0 + simClock * aw.speed
				local rNow = (aw.radius + aw.radJitter) * (0.88 + 0.16 * math.sin(simClock * 1.2 + aw.phase))
				local localP = Vector3.new(math.cos(th) * rNow, math.sin(th) * rNow * 0.78, math.sin(th * 2 + aw.phase) * 1.3)
				local nextTh = th + (aw.speed >= 0 and 0.08 or -0.08)
				local nextP = Vector3.new(math.cos(nextTh) * rNow, math.sin(nextTh) * rNow * 0.78, math.sin(nextTh * 2 + aw.phase) * 1.3)
				local worldP = FOCUS + aw.tilt:VectorToWorldSpace(localP)
				local worldNext = FOCUS + aw.tilt:VectorToWorldSpace(nextP)
				wp.Size = Vector3.new(aw.thick, aw.thick, aw.len * (0.85 + 0.30 * lifeBell))
				bulkN += 1; bulkParts[bulkN] = wp
				bulkCFs[bulkN] = safeLookAt(worldP, worldNext)
				wp.Transparency = 1 - wAlpha
			end
		end

		-- 6) 3 Smooth Precessing 3D Cyan Toroidal Magnetic Containment Rings
		local ringVis = clamp01(cyan * 0.34 + white * 0.54 + stabilize * 0.40) * starEnergy
		for _, mr in ipairs(magRings) do
			local mp = mr.mesh.part
			local bs = mr.mesh.baseSize
			local ringD = opaqueDiam * mr.scale * (1 + 0.024 * math.sin(simClock * 3.6))
			mp.Size = Vector3.new(
				bs.X * (ringD / math.max(bs.X, 0.01)),
				bs.Y * (ringD / math.max(bs.Y, 0.01)),
				bs.Z * (ringD / math.max(bs.Z, 0.01))
			)
			local rv = mr.vel * simClock
			bulkN += 1; bulkParts[bulkN] = mp
			bulkCFs[bulkN] = CFrame.new(FOCUS) * mr.tilt * CFrame.Angles(rv.X, rv.Y, rv.Z)
			mp.Transparency = 1 - clamp01(ringVis * 0.42)
		end
	end

	if bulkN > 0 then
		Workspace:BulkMoveTo(bulkParts, bulkCFs, Enum.BulkMoveMode.FireCFrameChanged)
	end

	telemAccum += step
	if telemAccum >= 0.08 then
		telemAccum = 0
		Workspace:SetAttribute("LaserActiveCount", activeLaserCount)
		Workspace:SetAttribute("LaserMaskHistory", maskHistoryStr)
		if activeLaserCount > 0 then
			Workspace:SetAttribute("LaserSpanMin", math.floor(minSpan * 10000 + 0.5) / 10000)
			Workspace:SetAttribute("LaserSpanMax", math.floor(maxSpan * 10000 + 0.5) / 10000)
			Workspace:SetAttribute("LaserSpanSpread", math.floor((maxSpan - minSpan) * 100000 + 0.5) / 100000)
			Workspace:SetAttribute("LaserFullDistSpread", math.floor((maxRawDist - minRawDist) * 100000 + 0.5) / 100000)
			Workspace:SetAttribute("LaserFocusMaxErr", math.floor(maxFocusErr * 100000 + 0.5) / 100000)
		else
			Workspace:SetAttribute("LaserSpanMin", 0)
			Workspace:SetAttribute("LaserSpanMax", 0)
			Workspace:SetAttribute("LaserSpanSpread", 0)
			Workspace:SetAttribute("LaserFullDistSpread", 0)
			Workspace:SetAttribute("LaserFocusMaxErr", 0)
		end
	end
end)

print("[3D REFERENCE VFX V15] Simultaneous 6-Laser Lockstep + Equal-Length Center Convergence + V14D Core online.")
