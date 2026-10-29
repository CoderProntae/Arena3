--!nonstrict
-- ============================================================================
-- FAZ 2 PAKET A — MULTI-TONE SLATE-IRON OCTAGONAL CHAMBER, 4 RADIAL SLIDING
-- HATCHES, 10-BLADE CNC REAR TURBINE & 18-STUD ENCLOSED EXHAUST PLENUM
-- ============================================================================
--   * 100% Real 3D MeshPart + SurfaceAppearance PBR (ZERO 2D ParticleEmitter /
--     Beam / BillboardGui; 0/8 live EditableMesh memory retained after boot!).
--   * Calibrated directly to 01_komut_110.jpg multi-tone cool slate-blue /
--     graphite-iron / olive-taupe industrial palette (ZERO coppery brown!).
--   * Preserves all 6 approved emitters, 6 pistons, V14D 3D nebula core, V15
--     simultaneous equal-length 6-laser ignition, and all gameplay controls.
-- ============================================================================

local AssetService = game:GetService("AssetService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local assembly = Workspace:WaitForChild("REACTOR_MESH_ASSEMBLY", 60)
local world = RunService:IsRunning()
	and Workspace:WaitForChild("CORE_PROTOCOL_V2_WORLD", 25)
	or Workspace:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
if not assembly then
	warn("[FAZ2] REACTOR_MESH_ASSEMBLY not found; skipping Faz 2 mount.")
	return
end
local staticRoot = assembly:WaitForChild("STATIC", 15)
local movingRoot = assembly:WaitForChild("MOVING", 15)
if not staticRoot or not movingRoot then return end

-- Clean idempotency if re-run
for _, container in ipairs({staticRoot, movingRoot}) do
	for _, ch in ipairs(container:GetChildren()) do
		if ch:GetAttribute("Faz2Generated") then
			ch:Destroy()
		end
	end
end

local ORIGIN_Y = 26.50
local FAN_X, FAN_Z = 0.0, 1.80
local FAN_HOLE_R = 3.92
local LOUVRE_X, LOUVRE_Z0, LOUVRE_Z1 = 3.76, 9.50, 12.50

-- Authoring (x, y_front_to_rear, z_up) -> Studio World (x, 26.50 + z, -y)
local function toStudioPos(x, y, z)
	return Vector3.new(x, ORIGIN_Y + z, -y)
end

local function toStudioVec(vx, vy, vz)
	local v = Vector3.new(vx, vz, -vy)
	local m = v.Magnitude
	return m > 1e-6 and (v / m) or Vector3.new(0, 0, 1)
end

local function hypot(a, b)
	return math.sqrt(a * a + b * b)
end

-- ============================================================================
-- 1. CALIBRATED MULTI-TONE SLATE-IRON / GRAPHITE / OLIVE-TAUPE PBR PALETTE
--    (Calibrated directly to 01_komut_110.jpg; 0 live EditableImage memory!)
-- ============================================================================
local MAT_DEFS = {
	iron_upper = {rgb = Color3.fromRGB(101, 113, 134), mat = Enum.Material.Metal, refl = 0.04},
	iron_mid   = {rgb = Color3.fromRGB( 74,  79,  94), mat = Enum.Material.Metal, refl = 0.03},
	iron_c4    = {rgb = Color3.fromRGB(101, 113, 134), mat = Enum.Material.Metal, refl = 0.04},
	iron_c3    = {rgb = Color3.fromRGB( 74,  79,  94), mat = Enum.Material.Metal, refl = 0.03},
	iron_c2    = {rgb = Color3.fromRGB( 65,  68,  78), mat = Enum.Material.Metal, refl = 0.03},
	iron_c1    = {rgb = Color3.fromRGB( 72,  69,  61), mat = Enum.Material.Metal, refl = 0.02},
	iron_lower = {rgb = Color3.fromRGB( 72,  69,  61), mat = Enum.Material.Metal, refl = 0.02},
	iron       = {rgb = Color3.fromRGB( 70,  75,  88), mat = Enum.Material.Metal, refl = 0.03},
	shroud     = {rgb = Color3.fromRGB( 70,  75,  88), mat = Enum.Material.Metal, refl = 0.06},
	blade      = {rgb = Color3.fromRGB( 56,  61,  73), mat = Enum.Material.Metal, refl = 0.08},
	plate      = {rgb = Color3.fromRGB( 86,  92, 104), mat = Enum.Material.Metal, refl = 0.05},
	radiator   = {rgb = Color3.fromRGB( 80,  76,  65), mat = Enum.Material.Metal, refl = 0.03},
	gunmetal   = {rgb = Color3.fromRGB( 46,  51,  60), mat = Enum.Material.Metal, refl = 0.03},
	tunnel     = {rgb = Color3.fromRGB( 38,  43,  52), mat = Enum.Material.Metal, refl = 0.02},
	frame      = {rgb = Color3.fromRGB( 44,  48,  56), mat = Enum.Material.Metal, refl = 0.03},
	lining     = {rgb = Color3.fromRGB( 42,  46,  55), mat = Enum.Material.Metal, refl = 0.02},
	rib        = {rgb = Color3.fromRGB( 46,  51,  60), mat = Enum.Material.Metal, refl = 0.03},
	weld       = {rgb = Color3.fromRGB( 54,  58,  68), mat = Enum.Material.Metal, refl = 0.03},
	pocket     = {rgb = Color3.fromRGB( 78,  83,  92), mat = Enum.Material.Metal, refl = 0.04},
	nickel     = {rgb = Color3.fromRGB(124, 132, 144), mat = Enum.Material.Metal, refl = 0.08},
	edge       = {rgb = Color3.fromRGB(164, 172, 184), mat = Enum.Material.Metal, refl = 0.10},
	cut        = {rgb = Color3.fromRGB(138, 145, 154), mat = Enum.Material.Metal, refl = 0.07},
	dark       = {rgb = Color3.fromRGB( 20,  24,  31), mat = Enum.Material.SmoothPlastic, refl = 0},
	hazard     = {rgb = Color3.fromRGB(206, 210, 216), mat = Enum.Material.SmoothPlastic, refl = 0},
	caution    = {rgb = Color3.fromRGB(192, 170,  58), mat = Enum.Material.SmoothPlastic, refl = 0},
	red        = {rgb = Color3.fromRGB(124,  52,  48), mat = Enum.Material.SmoothPlastic, refl = 0},
	sign       = {rgb = Color3.fromRGB( 52,  56,  64), mat = Enum.Material.Metal, refl = 0.02},
	lumen      = {rgb = Color3.fromRGB(228, 240, 252), mat = Enum.Material.Neon, refl = 0},
	worklight  = {rgb = Color3.fromRGB(218, 232, 248), mat = Enum.Material.Neon, refl = 0},
	blue_plenum= {rgb = Color3.fromRGB( 68, 144, 255), mat = Enum.Material.Neon, refl = 0},
	duct_lamp  = {rgb = Color3.fromRGB(214, 228, 246), mat = Enum.Material.Neon, refl = 0},
	cool_beacon= {rgb = Color3.fromRGB(172, 206, 248), mat = Enum.Material.Neon, refl = 0},
}

local function applyMat(part, matKey)
	local d = MAT_DEFS[matKey] or MAT_DEFS.gunmetal
	part.Color = d.rgb
	part.Material = d.mat
	part.Reflectance = d.refl or 0
end

-- ============================================================================
-- 2. ZERO-LEAK 3D MESH ACCUMULATOR (CENTERS BBOX -> EXACT 0.0000 STUD CFrame!)
-- ============================================================================
local MeshBin = {}
MeshBin.__index = MeshBin

function MeshBin.new()
	return setmetatable({buckets = {}}, MeshBin)
end

function MeshBin:getBucket(key)
	local b = self.buckets[key]
	if not b then
		b = {vs = {}, ns = {}, uvs = {}, fs = {}}
		self.buckets[key] = b
	end
	return b
end

-- Add authoring-space triangle mesh (v_list: { {x,y,z}, ... }, f_list: 1-based { {a,b,c}, ... })
function MeshBin:addRaw(key, v_list, f_list, hardCrease, uvScale)
	local b = self:getBucket(key)
	uvScale = uvScale or 12.0
	if hardCrease then
		for _, tri in ipairs(f_list) do
			local p1, p2, p3 = v_list[tri[1]], v_list[tri[2]], v_list[tri[3]]
			local s1 = toStudioPos(p1[1], p1[2], p1[3])
			local s2 = toStudioPos(p2[1], p2[2], p2[3])
			local s3 = toStudioPos(p3[1], p3[2], p3[3])
			local cr = (s2 - s1):Cross(s3 - s1)
			if cr.Magnitude > 1e-7 then
				local nrm = cr.Unit
				local base = #b.vs
				b.vs[base + 1] = s1; b.vs[base + 2] = s2; b.vs[base + 3] = s3
				b.ns[base + 1] = nrm; b.ns[base + 2] = nrm; b.ns[base + 3] = nrm
				b.uvs[base + 1] = Vector2.new((p1[1] + p1[2] * 0.5) / uvScale, (p1[3] + p1[2] * 0.3) / uvScale)
				b.uvs[base + 2] = Vector2.new((p2[1] + p2[2] * 0.5) / uvScale, (p2[3] + p2[2] * 0.3) / uvScale)
				b.uvs[base + 3] = Vector2.new((p3[1] + p3[2] * 0.5) / uvScale, (p3[3] + p3[2] * 0.3) / uvScale)
				b.fs[#b.fs + 1] = {base + 1, base + 2, base + 3}
			end
		end
	else
		local base = #b.vs
		local accN = table.create(#v_list, Vector3.zero)
		local stV = table.create(#v_list)
		for i, p in ipairs(v_list) do
			stV[i] = toStudioPos(p[1], p[2], p[3])
		end
		for _, tri in ipairs(f_list) do
			local i1, i2, i3 = tri[1], tri[2], tri[3]
			local cr = (stV[i2] - stV[i1]):Cross(stV[i3] - stV[i1])
			if cr.Magnitude > 1e-7 then
				accN[i1] += cr; accN[i2] += cr; accN[i3] += cr
				b.fs[#b.fs + 1] = {base + i1, base + i2, base + i3}
			end
		end
		for i, p in ipairs(v_list) do
			b.vs[base + i] = stV[i]
			local nm = accN[i]
			b.ns[base + i] = nm.Magnitude > 1e-7 and nm.Unit or Vector3.yAxis
			b.uvs[base + i] = Vector2.new((p[1] + 25.0) / uvScale, (p[3] + 22.0) / uvScale)
		end
	end
end

function MeshBin:box(key, cx, cy, cz, sx, sy, sz, rotCF_src)
	local hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
	local corners = {
		{-hx, -hy, -hz}, { hx, -hy, -hz}, { hx,  hy, -hz}, {-hx,  hy, -hz},
		{-hx, -hy,  hz}, { hx, -hy,  hz}, { hx,  hy,  hz}, {-hx,  hy,  hz},
	}
	local vs = {}
	for i, c in ipairs(corners) do
		if rotCF_src then
			local p = rotCF_src:PointToWorldSpace(Vector3.new(c[1], c[2], c[3]))
			vs[i] = {cx + p.X, cy + p.Y, cz + p.Z}
		else
			vs[i] = {cx + c[1], cy + c[2], cz + c[3]}
		end
	end
	local fs = {
		{1, 3, 2}, {1, 4, 3}, {5, 6, 7}, {5, 7, 8},
		{1, 2, 6}, {1, 6, 5}, {2, 3, 7}, {2, 7, 6},
		{3, 4, 8}, {3, 8, 7}, {4, 1, 5}, {4, 5, 8},
	}
	self:addRaw(key, vs, fs, true, 12.0)
end

function MeshBin:quad(key, pts)
	-- Extrude into a 0.036-stud 3D closed relief plate (ZERO coplanar 0-thickness back-to-back triangles!)
	local p1 = Vector3.new(pts[1][1], pts[1][2], pts[1][3])
	local p2 = Vector3.new(pts[2][1], pts[2][2], pts[2][3])
	local p3 = Vector3.new(pts[3][1], pts[3][2], pts[3][3])
	local p4 = Vector3.new(pts[4][1], pts[4][2], pts[4][3])
	local cr = (p2 - p1):Cross(p3 - p1)
	local n = cr.Magnitude > 1e-6 and cr.Unit or Vector3.yAxis
	local h = n * 0.018
	local vs = {
		{p1.X + h.X, p1.Y + h.Y, p1.Z + h.Z},
		{p2.X + h.X, p2.Y + h.Y, p2.Z + h.Z},
		{p3.X + h.X, p3.Y + h.Y, p3.Z + h.Z},
		{p4.X + h.X, p4.Y + h.Y, p4.Z + h.Z},
		{p1.X - h.X, p1.Y - h.Y, p1.Z - h.Z},
		{p2.X - h.X, p2.Y - h.Y, p2.Z - h.Z},
		{p3.X - h.X, p3.Y - h.Y, p3.Z - h.Z},
		{p4.X - h.X, p4.Y - h.Y, p4.Z - h.Z},
	}
	-- Verify winding in Studio space against centroid so every face points strictly outward
	local cSt = Vector3.zero
	for i = 1, 8 do cSt += toStudioPos(vs[i][1], vs[i][2], vs[i][3]) end
	cSt /= 8
	local rawFs = {
		{1, 2, 3}, {1, 3, 4},
		{5, 7, 6}, {5, 8, 7},
		{1, 5, 6}, {1, 6, 2},
		{2, 6, 7}, {2, 7, 3},
		{3, 7, 8}, {3, 8, 4},
		{4, 8, 5}, {4, 5, 1},
	}
	local fs = {}
	for _, tr in ipairs(rawFs) do
		local s1 = toStudioPos(vs[tr[1]][1], vs[tr[1]][2], vs[tr[1]][3])
		local s2 = toStudioPos(vs[tr[2]][1], vs[tr[2]][2], vs[tr[2]][3])
		local s3 = toStudioPos(vs[tr[3]][1], vs[tr[3]][2], vs[tr[3]][3])
		local fn = (s2 - s1):Cross(s3 - s1)
		local fc = (s1 + s2 + s3) / 3
		if fn:Dot(fc - cSt) >= 0 then
			fs[#fs + 1] = {tr[1], tr[2], tr[3]}
		else
			fs[#fs + 1] = {tr[1], tr[3], tr[2]}
		end
	end
	self:addRaw(key, vs, fs, true, 8.0)
end

function MeshBin:cyl(key, ax, ay, az, bx, by, bz, r, segs, hard)
	local dx, dy, dz = bx - ax, by - ay, bz - az
	local L = math.sqrt(dx * dx + dy * dy + dz * dz)
	if L < 1e-4 then return end
	local fwd = Vector3.new(dx / L, dy / L, dz / L)
	local ref = math.abs(fwd.Z) < 0.92 and Vector3.zAxis or Vector3.xAxis
	local uAx = fwd:Cross(ref).Unit
	local vAx = fwd:Cross(uAx).Unit
	local vs, fs = {}, {}
	for ring = 0, 1 do
		local ox = ring == 0 and ax or bx
		local oy = ring == 0 and ay or by
		local oz = ring == 0 and az or bz
		for j = 0, segs - 1 do
			local th = 2 * math.pi * j / segs
			local ct, st = math.cos(th) * r, math.sin(th) * r
			local p = uAx * ct + vAx * st
			vs[#vs + 1] = {ox + p.X, oy + p.Y, oz + p.Z}
		end
	end
	local c0 = #vs + 1; vs[c0] = {ax, ay, az}
	local c1 = #vs + 1; vs[c1] = {bx, by, bz}
	for j = 0, segs - 1 do
		local k = (j + 1) % segs
		local a, b, c, d = j + 1, k + 1, segs + j + 1, segs + k + 1
		fs[#fs + 1] = {a, b, d}; fs[#fs + 1] = {a, d, c}
	end
	self:addRaw(key, vs, fs, hard == true, 8.0)
	-- Flat endcaps with crisp rim normals
	local cap0, cap1, cf0, cf1 = {{ax, ay, az}}, {{bx, by, bz}}, {}, {}
	for j = 1, segs do
		cap0[j + 1] = vs[j]
		cap1[j + 1] = vs[segs + j]
	end
	for j = 1, segs do
		local k = (j % segs) + 1
		cf0[#cf0 + 1] = {1, k + 1, j + 1}
		cf1[#cf1 + 1] = {1, j + 1, k + 1}
	end
	self:addRaw(key, cap0, cf0, true, 8.0)
	self:addRaw(key, cap1, cf1, true, 8.0)
end

-- CNC 64-seg ring along Y_src around (cx, *, cz): smooth radial curvature + razor-sharp rim edges!
function MeshBin:annulus(key, y0, y1, r_in0, r_out0, r_in1, r_out1, segs, cx, cz)
	r_in1 = r_in1 or r_in0
	r_out1 = r_out1 or r_out0
	cx = cx or FAN_X; cz = cz or FAN_Z
	local specs = {
		{y0, r_in0, y0, r_out0, false, true},
		{y1, r_in1, y1, r_out1, true,  true},
		{y0, r_in0, y1, r_in1,  true,  false},
		{y0, r_out0,y1, r_out1, false, false},
	}
	for _, sp in ipairs(specs) do
		local ya, ra, yb, rb, flip, isFlat = sp[1], sp[2], sp[3], sp[4], sp[5], sp[6]
		if math.abs(ya - yb) > 1e-5 or math.abs(ra - rb) > 1e-5 then
			local vs, fs = {}, {}
			for ring = 0, 1 do
				local yv = ring == 0 and ya or yb
				local rv = ring == 0 and ra or rb
				for j = 0, segs - 1 do
					local th = 2 * math.pi * j / segs
					vs[#vs + 1] = {cx + rv * math.cos(th), yv, cz + rv * math.sin(th)}
				end
			end
			for j = 0, segs - 1 do
				local k = (j + 1) % segs
				local aa, bb, cc, dd = j + 1, k + 1, segs + j + 1, segs + k + 1
				if flip then
					fs[#fs + 1] = {aa, bb, cc}; fs[#fs + 1] = {bb, dd, cc}
				else
					fs[#fs + 1] = {aa, cc, bb}; fs[#fs + 1] = {bb, cc, dd}
				end
			end
			self:addRaw(key, vs, fs, isFlat, 8.0)
		end
	end
end

function MeshBin:emitToModel(parentModel, namePrefix, collide)
	local jobs = {}
	for key, b in pairs(self.buckets) do
		if #b.fs > 0 then
			jobs[#jobs + 1] = {key = key, b = b}
		end
	end
	local BATCH = 10
	local idx = 1
	while idx <= #jobs do
		local batchEnd = math.min(#jobs, idx + BATCH - 1)
		local remaining = batchEnd - idx + 1
		local caller = coroutine.running()
		local resumed = false
		for j = idx, batchEnd do
			local item = jobs[j]
			task.spawn(function()
				local okRun, errRun = pcall(function()
					local key, b = item.key, item.b
					local minX, minY, minZ = math.huge, math.huge, math.huge
					local maxX, maxY, maxZ = -math.huge, -math.huge, -math.huge
					for _, v in ipairs(b.vs) do
						if v.X < minX then minX = v.X end; if v.X > maxX then maxX = v.X end
						if v.Y < minY then minY = v.Y end; if v.Y > maxY then maxY = v.Y end
						if v.Z < minZ then minZ = v.Z end; if v.Z > maxZ then maxZ = v.Z end
					end
					local center = Vector3.new((minX + maxX) * 0.5, (minY + maxY) * 0.5, (minZ + maxZ) * 0.5)
					local em = AssetService:CreateEditableMesh()
					local vids = table.create(#b.vs)
					local nids = table.create(#b.vs)
					local uvids = table.create(#b.vs)
					for i = 1, #b.vs do
						vids[i] = em:AddVertex(b.vs[i] - center)
						nids[i] = em:AddNormal(b.ns[i])
						uvids[i] = em:AddUV(b.uvs[i])
					end
					for _, tri in ipairs(b.fs) do
						local i1, i2, i3 = tri[1], tri[2], tri[3]
						local fid = em:AddTriangle(vids[i1], vids[i2], vids[i3])
						em:SetFaceNormals(fid, {nids[i1], nids[i2], nids[i3]})
						em:SetFaceUVs(fid, {uvids[i1], uvids[i2], uvids[i3]})
					end
					local ok, st, content = pcall(function()
						return AssetService:CreateDataModelContentAsync(Content.fromObject(em))
					end)
					local mp
					if ok and st == Enum.CreateContentResult.Success and content then
						pcall(function() em:Destroy() end)
						mp = AssetService:CreateMeshPartAsync(content)
					else
						mp = AssetService:CreateMeshPartAsync(Content.fromObject(em))
						pcall(function() em:Destroy() end)
					end
					mp.Name = namePrefix .. "__" .. key
					mp.Anchored = true
					mp.CanCollide = collide == true
					mp.CanTouch = false
					mp.CanQuery = false
					mp.CastShadow = (key ~= "lumen" and key ~= "worklight" and key ~= "blue_plenum" and key ~= "duct_lamp")
					mp.CFrame = CFrame.new(center)
					applyMat(mp, key)
					mp.Parent = parentModel
				end)
				if not okRun then warn("[FAZ2] emit err:", errRun) end
				remaining -= 1
				if remaining == 0 and not resumed then
					resumed = true
					task.spawn(caller)
				end
			end)
		end
		if remaining > 0 and not resumed then
			coroutine.yield()
		end
		idx = batchEnd + 1
	end
end

local function makeSubModel(parent, name)
	local m = Instance.new("Model")
	m.Name = name
	m:SetAttribute("Faz2Generated", true)
	m.Parent = parent
	return m
end

-- ============================================================================
-- 3. BUILD REV05 MULTI-TONE SLATE-IRON REAR BULKHEAD (WITH CIRCULAR FAN PORT!)
-- ============================================================================
do
	local outerOct = {
		{-17.0, -21.5}, {17.0, -21.5}, {24.5, -12.5}, {24.5, 12.5},
		{17.0, 21.5}, {-17.0, 21.5}, {-24.5, 12.5}, {-24.5, -12.5},
	}
	local function bendY(x)
		local t = math.clamp((math.abs(x) - 16.14) / (24.5 - 16.14), 0, 1)
		return -2.55 * t * t * (3 - 2 * t)
	end
	local function apWeight(x, z)
		local dist = 1e6
		for _, c in ipairs({-10.75, 10.75}) do
			local dx = math.max(c - 5.36 - x, 0, x - (c + 5.36))
			local dz = math.max(-7.18 - z, 0, z - 17.18)
			dist = math.min(dist, math.sqrt(dx * dx + dz * dz))
		end
		local t = math.clamp(1.0 - dist / 1.22, 0, 1)
		return t * t * (3 - 2 * t)
	end
	local function wallY(x, z)
		local q = math.clamp((z - 9.0) / 4.5, 0, 1)
		q = q * q * (3 - 2 * q)
		return bendY(x) - (1.50 * (1 - q) + 0.12 * q) * apWeight(x, z)
	end
	local function clipHP(poly, ax, az, bx, bz)
		local out = {}
		local n = #poly
		for i = 1, n do
			local s = poly[i]
			local e = poly[(i % n) + 1]
			local ds = (bx - ax) * (s[2] - az) - (bz - az) * (s[1] - ax)
			local de = (bx - ax) * (e[2] - az) - (bz - az) * (e[1] - ax)
			local ins, ine = ds >= -1e-7, de >= -1e-7
			if ins ~= ine then
				local q = ds / (ds - de)
				out[#out + 1] = {s[1] + (e[1] - s[1]) * q, s[2] + (e[2] - s[2]) * q}
			end
			if ine then out[#out + 1] = e end
		end
		local clean = {}
		for _, p in ipairs(out) do
			if #clean == 0 or hypot(p[1] - clean[#clean][1], p[2] - clean[#clean][2]) > 1e-5 then
				clean[#clean + 1] = p
			end
		end
		if #clean > 1 and hypot(clean[1][1] - clean[#clean][1], clean[1][2] - clean[#clean][2]) < 1e-5 then
			table.remove(clean)
		end
		return clean
	end
	local function clipOct(poly)
		for i = 1, #outerOct do
			if #poly == 0 then break end
			local a, b = outerOct[i], outerOct[(i % #outerOct) + 1]
			poly = clipHP(poly, a[1], a[2], b[1], b[2])
		end
		return poly
	end

	local BOX_X = 4.10
	local BOX_Z0, BOX_Z1 = FAN_Z - 4.10, FAN_Z + 4.10
	local xcuts = {-24.5, -17.74, -17.34, -17.0, -16.74, -16.44, -16.14,
	               -5.36, -5.06, -4.76, -BOX_X, -LOUVRE_X, 0.0, LOUVRE_X, BOX_X, 4.76, 5.06, 5.36,
	               16.14, 16.44, 16.74, 17.0, 17.34, 17.74, 24.5}
	local zcuts = {-21.5, -12.5, -8.78, -8.38, -7.98, -7.78, -7.48, -7.18, BOX_Z0, -2.0,
	               BOX_Z1, 8.5, 9.50, 11.0, 12.50, 13.5, 17.18, 17.48, 17.78, 18.18, 18.78, 21.5}
	local bands = {-21.5, -12.5, -2.0, 8.5, 21.5}

	local rawPolys = {}
	for i = 1, #xcuts - 1 do
		local x1, x2 = xcuts[i], xcuts[i + 1]
		for j = 1, #zcuts - 1 do
			local z1, z2 = zcuts[j], zcuts[j + 1]
			local gHole = (((x1 >= 5.36 - 1e-5 and x2 <= 16.14 + 1e-5) or (x1 >= -16.14 - 1e-5 and x2 <= -5.36 + 1e-5))
				and z1 >= -7.18 - 1e-5 and z2 <= 17.18 + 1e-5)
			local lHole = (x1 >= -LOUVRE_X - 1e-5 and x2 <= LOUVRE_X + 1e-5 and z1 >= LOUVRE_Z0 - 1e-5 and z2 <= LOUVRE_Z1 + 1e-5)
			local fBox = (x1 >= -BOX_X - 1e-5 and x2 <= BOX_X + 1e-5 and z1 >= BOX_Z0 - 1e-5 and z2 <= BOX_Z1 + 1e-5)
			if not (gHole or lHole or fBox) then
				rawPolys[#rawPolys + 1] = {{x1, z1}, {x2, z1}, {x2, z2}, {x1, z2}}
			end
		end
	end
	local N_FAN = 48
	for k = 0, N_FAN - 1 do
		local th0 = 2 * math.pi * k / N_FAN
		local th1 = 2 * math.pi * (k + 1) / N_FAN
		local thM = 0.5 * (th0 + th1)
		local function sqPt(th)
			local c, s = math.cos(th), math.sin(th)
			local sc = BOX_X / math.max(math.abs(c), math.abs(s))
			return {c * sc, FAN_Z + s * sc}
		end
		local ci0 = {FAN_HOLE_R * math.cos(th0), FAN_Z + FAN_HOLE_R * math.sin(th0)}
		local ciM = {FAN_HOLE_R * math.cos(thM), FAN_Z + FAN_HOLE_R * math.sin(thM)}
		local ci1 = {FAN_HOLE_R * math.cos(th1), FAN_Z + FAN_HOLE_R * math.sin(th1)}
		for _, ap in ipairs({{ci0, sqPt(th0), sqPt(thM), ciM}, {ciM, sqPt(thM), sqPt(th1), ci1}}) do
			local ab = clipHP(ap, -10, -2.0, 10, -2.0)
			local bl = clipHP(ap, 10, -2.0, -10, -2.0)
			if #ab >= 3 then rawPolys[#rawPolys + 1] = ab end
			if #bl >= 3 then rawPolys[#rawPolys + 1] = bl end
		end
	end

	local function extrudePolys(bin, matKey, items, frontY, backY, isLiner)
		local vs, fidx, bidx, fs, backOf = {}, {}, {}, {}, {}
		local function getV(x, z, back)
			local key = string.format("%.4f_%.4f", x, z)
			local cache = back and bidx or fidx
			local id = cache[key]
			if not id then
				local y = (back and backY or frontY) + wallY(x, z)
				if isLiner and not back then y -= 0.35 * apWeight(x, z) end
				id = #vs + 1
				vs[id] = {x, y, z}
				cache[key] = id
			end
			return id
		end
		local frontTris = {}
		for _, poly in ipairs(items) do
			if #poly >= 3 then
				local a, b = {}, {}
				for i, p in ipairs(poly) do
					a[i] = getV(p[1], p[2], false)
					b[i] = getV(p[1], p[2], true)
					backOf[a[i]] = b[i]
				end
				for j = 2, #poly - 1 do
					if a[1] ~= a[j] and a[j] ~= a[j + 1] and a[1] ~= a[j + 1] then
						frontTris[#frontTris + 1] = {a[1], a[j], a[j + 1]}
						fs[#fs + 1] = {a[1], a[j], a[j + 1]}
						fs[#fs + 1] = {b[1], b[j + 1], b[j]}
					end
				end
			end
		end
		local edgeUses = {}
		for _, t in ipairs(frontTris) do
			for _, pr in ipairs({{t[1], t[2]}, {t[2], t[3]}, {t[3], t[1]}}) do
				local u, v = pr[1], pr[2]
				local k = u < v and (u .. "_" .. v) or (v .. "_" .. u)
				if not edgeUses[k] then edgeUses[k] = {} end
				table.insert(edgeUses[k], pr)
			end
		end
		for _, uses in pairs(edgeUses) do
			if #uses == 1 then
				local u, v = uses[1][1], uses[1][2]
				local U, V = backOf[u], backOf[v]
				fs[#fs + 1] = {u, v, V}; fs[#fs + 1] = {u, V, U}
			end
		end
		bin:addRaw(matKey, vs, fs, false, 48.0)
	end

	local binR5 = MeshBin.new()
	local linerPolys = {}
	local cPolys = {{}, {}, {}, {}}
	for _, rp in ipairs(rawPolys) do
		local q = clipOct(rp)
		if #q >= 3 then
			linerPolys[#linerPolys + 1] = q
			local cz = 0
			for _, p in ipairs(q) do cz += p[2] end
			cz /= #q
			local band = 1
			for bi = 1, 4 do
				if cz >= bands[bi] - 1e-4 and cz <= bands[bi + 1] + 1e-4 then band = bi; break end
			end
			local zLo = bands[band] + (band > 1 and 0.060 or -1.0)
			local zHi = bands[band + 1] - (band < 4 and 0.060 or -1.0)
			local q2 = clipHP(clipHP(q, -30, zLo, 30, zLo), 30, zHi, -30, zHi)
			if #q2 >= 3 then table.insert(cPolys[band], q2) end
		end
	end
	extrudePolys(binR5, "lining", linerPolys, 15.48, 16.12, true)
	for bi = 1, 4 do
		extrudePolys(binR5, "iron_c" .. bi, cPolys[bi], 15.13, 15.40, false)
	end
	for _, z in ipairs({-12.5, -2.0, 8.5}) do
		local spans = math.abs(z + 2.0) < 0.1 and {{-23.8, -16.35}, {-5.10, -3.95}, {3.95, 5.10}, {16.35, 23.8}}
			or (z < -7.18 and {{-23.8, 23.8}} or {{-23.8, -16.35}, {-5.10, 5.10}, {16.35, 23.8}})
		for _, sp in ipairs(spans) do
			for s = 0, 4 do
				local x0 = sp[1] + (sp[2] - sp[1]) * (s / 5)
				local x1 = sp[1] + (sp[2] - sp[1]) * ((s + 1) / 5)
				binR5:cyl("weld", x0, 15.14 + bendY(x0), z, x1, 15.14 + bendY(x1), z, 0.032, 6, false)
			end
		end
	end
	for _, sgn in ipairs({-1, 1}) do
		local xw = sgn * 17.0
		binR5:cyl("cut", xw, 15.04 + bendY(xw), -12.45, xw, 15.04 + bendY(xw), 12.45, 0.067, 8, false)
		local xs = sgn * 21.12; local bd = bendY(xs)
		binR5:box("rib", xs, 15.08 + bd, 3.4, 0.30, 0.33, 13.8)
		for k = 0, 9 do
			local xx = sgn * 10.75 - 3.97 + k * 0.85
			binR5:cyl("caution", xx - 0.14, 15.03, -8.07, xx + 0.10, 15.03, -7.94, 0.047, 6, true)
		end
	end
	for i = 1, #outerOct do
		local a, b = outerOct[i], outerOct[(i % #outerOct) + 1]
		binR5:cyl("rib", a[1], 15.03 + bendY(a[1]), a[2], b[1], 15.03 + bendY(b[1]), b[2], 0.096, 8, false)
	end

	local mRev05 = makeSubModel(staticRoot, "REACTOR_REAR_BULKHEAD_REV05_TURBINE_PORT")
	binR5:emitToModel(mRev05, "REV05")
end

-- ============================================================================
-- 4. BUILD 10-BLADE RAZOR-SHARP CNC TURBINE + 18-STUD ENCLOSED PLENUM
-- ============================================================================
local rotorModel = makeSubModel(movingRoot, "REACTOR_REAR_TURBINE_ROTOR")
local rotorPivotStudio = toStudioPos(FAN_X, 16.25, FAN_Z)
do
	local binPlenum = MeshBin.new()
	local binRotor = MeshBin.new()

	local function wallY_center(x, z)
		local dist = math.min(
			hypot(math.max(-10.75 - 5.36 - x, 0, x - (-10.75 + 5.36)), math.max(-7.18 - z, 0, z - 17.18)),
			hypot(math.max( 10.75 - 5.36 - x, 0, x - ( 10.75 + 5.36)), math.max(-7.18 - z, 0, z - 17.18))
		)
		local t = math.clamp(1.0 - dist / 1.22, 0, 1)
		local w = t * t * (3 - 2 * t)
		local q = math.clamp((z - 9.0) / 4.5, 0, 1); q = q * q * (3 - 2 * q)
		return -(1.50 * (1 - q) + 0.12 * q) * w
	end

	-- A) 64-seg Stepped CNC Intake Cowling + 24 Hex Bolts + Flanking Stripes
	binPlenum:annulus("shroud", 14.88, 15.34, 3.90, 4.52, 3.90, 4.56, 64)
	binPlenum:annulus("edge",   14.80, 14.89, 4.38, 4.50, 4.44, 4.54, 64)
	binPlenum:annulus("edge",   14.72, 14.88, 3.74, 3.98, 3.88, 4.18, 64)
	binPlenum:annulus("dark",   14.86, 15.48, 3.68, 3.76, 3.68, 3.76, 64)
	binPlenum:annulus("shroud", 15.46, 17.00, 3.70, 3.94, 3.70, 3.94, 64)
	binPlenum:annulus("edge",   15.52, 15.66, 3.64, 3.71, 3.64, 3.71, 64)
	for j = 0, 23 do
		local th = 2 * math.pi * j / 24
		local bx, bz = FAN_X + 4.24 * math.cos(th), FAN_Z + 4.24 * math.sin(th)
		binPlenum:cyl("edge", bx, 14.78, bz, bx, 14.90, bz, 0.072, 6, true)
	end
	for _, side in ipairs({-1, 1}) do
		local sx = side * 4.62
		local wyM = 15.13 + wallY_center(sx, FAN_Z)
		binPlenum:box("dark", sx, wyM - 0.06, FAN_Z + 0.1, 0.44, 0.08, 7.2)
		local sz = FAN_Z - 3.1
		while sz <= FAN_Z + 3.15 do
			local wy0 = 15.13 + wallY_center(sx, sz) - 0.12
			local wy1 = 15.13 + wallY_center(sx, sz + 0.54) - 0.12
			binPlenum:quad("hazard", {
				{sx - 0.19, wy0, sz}, {sx + 0.19, wy0, sz + 0.26},
				{sx + 0.19, wy1, sz + 0.58}, {sx - 0.19, wy1, sz + 0.32},
			})
			sz += 0.86
		end
	end

	-- B) Upper Recessed Cobalt-Blue Louvered Cooling Intake Vent
	local lvZc, lvZh = 0.5 * (LOUVRE_Z0 + LOUVRE_Z1), (LOUVRE_Z1 - LOUVRE_Z0)
	binPlenum:box("shroud", 0, 15.42, LOUVRE_Z1 + 0.16, LOUVRE_X * 2 + 0.68, 1.35, 0.32)
	binPlenum:box("shroud", 0, 15.42, LOUVRE_Z0 - 0.16, LOUVRE_X * 2 + 0.68, 1.35, 0.32)
	binPlenum:box("shroud", -LOUVRE_X - 0.18, 15.42, lvZc, 0.36, 1.35, lvZh + 0.64)
	binPlenum:box("shroud",  LOUVRE_X + 0.18, 15.42, lvZc, 0.36, 1.35, lvZh + 0.64)
	binPlenum:box("dark", 0, 16.55, lvZc, LOUVRE_X * 2 + 0.36, 1.70, lvZh + 0.32)
	binPlenum:box("blue_plenum", 0, 15.62, lvZc, LOUVRE_X * 2 - 0.12, 0.12, lvZh - 0.12)
	for _, mx in ipairs({-1.35, 1.35}) do
		binPlenum:box("shroud", mx, 15.36, lvZc, 0.12, 0.65, lvZh - 0.08)
	end
	local slatRot = CFrame.Angles(math.rad(-14), 0, 0)
	for i = 0, 6 do
		local lz = (LOUVRE_Z0 + 0.32) + ((LOUVRE_Z1 - 0.32) - (LOUVRE_Z0 + 0.32)) * (i / 6)
		binPlenum:box("edge", 0, 15.35, lz, LOUVRE_X * 2 - 0.12, 0.22, 0.052, slatRot)
	end
	-- Armored Ribbed Rear HVAC Exhaust Trunk connecting Upper Louver -> Rear Condenser Plenum Roof (%0 floating rear box!)
	do
		local dW = LOUVRE_X * 2 + 0.72
		local dH = lvZh + 0.68
		-- Horizontal armored duct run (Y_src = 16.05 .. 31.35)
		binPlenum:box("tunnel", 0, 23.70, lvZc, dW, 15.30, dH)
		-- Stiffener flange ribs along the horizontal HVAC duct
		for _, yRib in ipairs({16.35, 19.10, 21.85, 24.60, 27.35, 30.10}) do
			binPlenum:box("shroud", 0, yRib, lvZc, dW + 0.42, 0.34, dH + 0.42)
		end
		-- 90-degree vertical drop trunk (Y_src = 28.45 .. 31.35, Z_src = 7.45 .. lvZc + dH*0.5) bolted straight into Condenser Plenum Roof!
		local zTop = lvZc + dH * 0.5
		local zBot = 7.45
		binPlenum:box("tunnel", 0, 29.90, 0.5 * (zTop + zBot), dW, 2.95, zTop - zBot)
		binPlenum:box("shroud", 0, 29.90, 7.72, dW + 0.68, 3.55, 0.38) -- Heavy bolted condenser roof collar flange
		binPlenum:box("shroud", 0, 31.46, 0.5 * (zTop + zBot), dW + 0.30, 0.28, (zTop - zBot) + 0.24) -- Rear miter cap plate
		-- Side gusset brackets tying the HVAC trunk to the rear bulkhead & condenser roof
		for _, sx in ipairs({-1, 1}) do
			binPlenum:cyl("frame", sx * (dW * 0.46), 16.40, LOUVRE_Z0 - 0.18, sx * (dW * 0.46), 20.40, 6.25, 0.16, 10, true)
		end
	end

	-- C) 10-Blade Razor-Sharp CNC Turbine Rotor + Solid CNC Rear Drive Shaft (Separately Animated Model!)
	local RY = 16.25
	binRotor:annulus("shroud", RY - 0.40, RY + 0.66, 0.02, 1.12, 0.02, 1.12, 48)
	binRotor:annulus("edge",   RY - 0.48, RY - 0.38, 0.76, 1.08, 0.80, 1.12, 48)
	binRotor:annulus("shroud", RY - 0.86, RY - 0.46, 0.02, 0.56, 0.02, 0.74, 48)
	binRotor:annulus("nickel", RY - 0.96, RY - 0.84, 0.16, 0.34, 0.16, 0.42, 32)
	binRotor:cyl("edge", FAN_X, RY - 1.02, FAN_Z, FAN_X, RY - 0.86, FAN_Z, 0.15, 6, true)
	-- Solid CNC Chrome-Nickel Main Drive Shaft + Rear Splined Hub Collar plunging directly into Stator Thrust Bearing (%0 air gap!)
	binRotor:annulus("edge",   RY + 0.58, RY + 0.86, 0.50, 0.88, 0.50, 0.84, 32)
	binRotor:cyl("nickel", FAN_X, RY - 0.20, FAN_Z, FAN_X, 18.05, FAN_Z, 0.54, 24, true)
	for sb = 0, 7 do
		local sth = 2 * math.pi * sb / 8
		binRotor:cyl("edge", FAN_X + 0.72 * math.cos(sth), RY + 0.82, FAN_Z + 0.72 * math.sin(sth),
			FAN_X + 0.72 * math.cos(sth), RY + 0.92, FAN_Z + 0.72 * math.sin(sth), 0.055, 6, true)
	end

	local N_BLADES = 10
	for hb = 0, N_BLADES - 1 do
		local hth = 2 * math.pi * (hb + 0.5) / N_BLADES
		local hx, hz = FAN_X + 0.92 * math.cos(hth), FAN_Z + 0.92 * math.sin(hth)
		binRotor:cyl("edge", hx, RY - 0.54, hz, hx, RY - 0.44, hz, 0.058, 6, true)
	end
	for b_i = 0, N_BLADES - 1 do
		local ang = 2 * math.pi * b_i / N_BLADES + math.rad(10)
		local ca, sa = math.cos(ang), math.sin(ang)
		binRotor:cyl("nickel", FAN_X + 1.04 * ca, RY + 0.02, FAN_Z + 1.04 * sa, FAN_X + 1.32 * ca, RY + 0.02, FAN_Z + 1.32 * sa, 0.22, 16, false)

		local rRoot, rTip = 1.22, 3.58
		local nS = 8
		local bv, bf, lev, lef = {}, {}, {}, {}
		for s = 0, nS - 1 do
			local u = s / (nS - 1)
			local rS = rRoot + (rTip - rRoot) * u
			local ch = 1.02 * (1 - u) + 0.54 * u
			local pt = math.rad(36) * (1 - u) + math.rad(24) * u
			local thk = 0.115 * (1 - 0.42 * u)
			local dy, dt = 0.5 * ch * math.sin(pt), 0.5 * ch * math.cos(pt)
			local nyC, ntC = -math.cos(pt), math.sin(pt)
			local profM = {
				{-0.72 * dy + nyC * thk * 0.45, -0.72 * dt + ntC * thk * 0.45},
				{-0.10 * dy + nyC * thk * 0.55, -0.10 * dt + ntC * thk * 0.55},
				{ 0.85 * dy + nyC * thk * 0.18,  0.85 * dt + ntC * thk * 0.18},
				{ 1.00 * dy,                     1.00 * dt},
				{ 0.85 * dy - nyC * thk * 0.18,  0.85 * dt - ntC * thk * 0.18},
				{-0.72 * dy - nyC * thk * 0.45, -0.72 * dt - ntC * thk * 0.45},
			}
			for _, pr in ipairs(profM) do
				bv[#bv + 1] = {FAN_X + rS * ca - pr[2] * sa, RY + pr[1], FAN_Z + rS * sa + pr[2] * ca}
			end
			local profL = {
				{-1.02 * dy, -1.02 * dt},
				{-0.70 * dy + nyC * thk * 0.47, -0.70 * dt + ntC * thk * 0.47},
				{-0.70 * dy - nyC * thk * 0.47, -0.70 * dt - ntC * thk * 0.47},
			}
			for _, pr in ipairs(profL) do
				lev[#lev + 1] = {FAN_X + rS * ca - pr[2] * sa, RY + pr[1], FAN_Z + rS * sa + pr[2] * ca}
			end
		end
		for s = 0, nS - 2 do
			local o0, o1 = s * 6, (s + 1) * 6
			for q = 0, 5 do
				local qn = (q + 1) % 6
				bf[#bf + 1] = {o0 + q + 1, o1 + q + 1, o1 + qn + 1}
				bf[#bf + 1] = {o0 + q + 1, o1 + qn + 1, o0 + qn + 1}
			end
		end
		local lt = (nS - 1) * 6
		for q = 1, 4 do
			bf[#bf + 1] = {1, q + 2, q + 1}
			bf[#bf + 1] = {lt + 1, lt + q + 1, lt + q + 2}
		end
		binRotor:addRaw("blade", bv, bf, true, 6.0)

		for s = 0, nS - 2 do
			local o0, o1 = s * 3, (s + 1) * 3
			for q = 0, 2 do
				local qn = (q + 1) % 3
				lef[#lef + 1] = {o0 + q + 1, o1 + q + 1, o1 + qn + 1}
				lef[#lef + 1] = {o0 + q + 1, o1 + qn + 1, o0 + qn + 1}
			end
		end
		local ltL = (nS - 1) * 3
		lef[#lef + 1] = {1, 3, 2}; lef[#lef + 1] = {ltL + 1, ltL + 2, ltL + 3}
		binRotor:addRaw("edge", lev, lef, true, 6.0)
	end

	-- D) Deep 18-Stud Behind-Fan Stator, Thrust Bearing, Dual 8-Strut Spiders, Tunnel Skid & Condenser Plenum (%0 Void!)
	binPlenum:annulus("tunnel", 15.55, 27.05, 3.92, 4.34, 3.92, 4.34, 48)
	for ri = 0, 6 do
		local yr = 17.4 + (26.1 - 17.4) * (ri / 6)
		binPlenum:annulus("shroud", yr - 0.14, yr + 0.14, 3.68, 3.94, 3.68, 3.94, 44)
		-- Exterior tunnel circumferential stiffener rings & saddle cradles onto structural skid beams!
		binPlenum:annulus("shroud", yr - 0.16, yr + 0.16, 4.32, 4.58, 4.32, 4.58, 40)
	end
	for _, sx in ipairs({-2.85, 2.85}) do
		binPlenum:box("frame", sx, 21.30, FAN_Z - 4.45, 0.72, 11.40, 0.68)
		for _, yPost in ipairs({17.4, 21.3, 25.2}) do
			binPlenum:box("shroud", sx, yPost, FAN_Z - 3.65, 0.64, 0.62, 1.35)
		end
	end
	-- Front Flanged Thrust Bearing Seal Housing (mates directly around the rotating 0.54-radius shaft at Y_src = 16.96..17.48!)
	binPlenum:annulus("nickel", 16.96, 17.22, 0.55, 1.06, 0.55, 1.18, 32)
	binPlenum:annulus("shroud", 17.18, 17.56, 0.55, 1.36, 0.55, 1.36, 36)
	for bb = 0, 11 do
		local bth = 2 * math.pi * bb / 12
		binPlenum:cyl("edge", FAN_X + 1.18 * math.cos(bth), 17.10, FAN_Z + 1.18 * math.sin(bth),
			FAN_X + 1.18 * math.cos(bth), 17.24, FAN_Z + 1.18 * math.sin(bth), 0.055, 6, true)
	end
	-- Main Stator Motor Nacelle (capped solid at both ends + rear flanged end-bell!)
	binPlenum:cyl("shroud", FAN_X, 17.45, FAN_Z, FAN_X, 23.10, FAN_Z, 1.16, 32, true)
	binPlenum:annulus("nickel", 18.10, 19.85, 1.15, 1.30, 1.15, 1.30, 32)
	binPlenum:annulus("nickel", 21.40, 22.85, 1.15, 1.28, 1.15, 1.28, 32)
	binPlenum:cyl("edge", FAN_X, 23.10, FAN_Z, FAN_X, 24.55, FAN_Z, 0.74, 24, true)
	binPlenum:annulus("shroud", 24.35, 24.68, 0.36, 0.92, 0.36, 0.92, 24)

	-- Dual Heavy 8-Vane Structural Stator Spiders (Front Y=17.75 & Rear Y=22.35) welding Motor Nacelle to Tunnel Shell!
	for _, ySp in ipairs({17.75, 22.35}) do
		for si = 0, 7 do
			local th = 2 * math.pi * si / 8 + math.pi / 8
			local rMid = 2.52
			local c, s = math.cos(th), math.sin(th)
			local stRot = CFrame.fromMatrix(
				Vector3.zero,
				Vector3.new(c, 0, s),
				Vector3.new(0, 1, 0),
				Vector3.new(-s, 0, c)
			)
			binPlenum:box("shroud", FAN_X + rMid * c, ySp, FAN_Z + rMid * s, 2.86, 0.78, 0.24, stRot)
			binPlenum:box("nickel", FAN_X + rMid * c, ySp - 0.34, FAN_Z + rMid * s, 2.78, 0.14, 0.30, stRot)
		end
	end

	-- Rear Axial Thrust A-Frame & Twin Armored Power/Lube Trunks anchoring Motor Tail (24.50) into Condenser Plenum Cross-Girder (27.20)!
	binPlenum:box("shroud", 0, 27.15, FAN_Z, 8.20, 0.72, 1.10) -- Heavy horizontal condenser intake cross-beam
	binPlenum:cyl("nickel", FAN_X, 24.50, FAN_Z, FAN_X, 27.25, FAN_Z, 0.42, 18, true) -- Central thrust column
	for _, sx in ipairs({-1, 1}) do
		binPlenum:cyl("frame", FAN_X + sx * 0.52, 24.35, FAN_Z + 0.28, FAN_X + sx * 2.45, 27.10, FAN_Z + 0.55, 0.18, 12, true)
		binPlenum:cyl("frame", FAN_X + sx * 0.52, 24.35, FAN_Z - 0.28, FAN_X + sx * 2.45, 27.10, FAN_Z - 0.55, 0.18, 12, true)
	end

	for _, deg in ipairs({35, 145, 215, 325}) do
		local th = math.rad(deg)
		local px, pz = FAN_X + 3.52 * math.cos(th), FAN_Z + 3.52 * math.sin(th)
		binPlenum:cyl(deg < 180 and "nickel" or "edge", px, 16.40, pz, px, 29.80, pz, 0.15, 12, true)
	end
	binPlenum:box("shroud", FAN_X, 22.5, FAN_Z - 2.95, 2.35, 11.4, 0.18)
	for ri = 0, 13 do
		local yr = 17.2 + (27.4 - 17.2) * (ri / 13)
		binPlenum:box("edge", FAN_X, yr, FAN_Z - 2.84, 2.20, 0.14, 0.06)
	end
	for _, sgn in ipairs({-1, 1}) do
		binPlenum:box("shroud", sgn * 3.58, 20.8, FAN_Z + 0.85, 0.18, 4.6, 0.42)
		binPlenum:box("duct_lamp", sgn * 3.48, 20.8, FAN_Z + 0.85, 0.08, 4.2, 0.22)
	end
	binPlenum:box("cool_beacon", FAN_X, 24.8, FAN_Z + 3.48, 0.95, 1.8, 0.10)

	local PL_X, PL_Z0, PL_Z1 = 6.60, -3.80, 7.60
	local PL_ZC, PL_ZH = 0.5 * (PL_Z0 + PL_Z1), (PL_Z1 - PL_Z0)
	binPlenum:box("tunnel", -5.225, 26.85, PL_ZC, 2.75, 0.55, PL_ZH)
	binPlenum:box("tunnel",  5.225, 26.85, PL_ZC, 2.75, 0.55, PL_ZH)
	binPlenum:box("tunnel", 0, 26.85, PL_Z1 - 0.85, PL_X * 2, 0.55, 1.75)
	binPlenum:box("tunnel", 0, 26.85, PL_Z0 + 0.85, PL_X * 2, 0.55, 1.75)
	binPlenum:box("tunnel", -PL_X, 30.5, PL_ZC, 0.55, 7.6, PL_ZH)
	binPlenum:box("tunnel",  PL_X, 30.5, PL_ZC, 0.55, 7.6, PL_ZH)
	binPlenum:box("tunnel", 0, 30.5, PL_Z1, PL_X * 2 + 0.55, 7.6, 0.55)
	binPlenum:box("tunnel", 0, 30.5, PL_Z0, PL_X * 2 + 0.55, 7.6, 0.55)
	binPlenum:box("shroud", 0, 34.10, PL_ZC, PL_X * 2 + 0.55, 0.65, PL_ZH + 0.55)
	for ti = 0, 11 do
		local hx = -5.1 + 10.2 * (ti / 11)
		local yt = math.abs(hx) > 1.8 and 29.6 or 31.2
		binPlenum:cyl("blade", hx, yt, PL_Z0 + 0.4, hx, yt, PL_Z1 - 0.4, 0.24, 12, false)
		for fi = 0, 8 do
			local fz = (PL_Z0 + 1.0) + ((PL_Z1 - 1.0) - (PL_Z0 + 1.0)) * (fi / 8)
			binPlenum:cyl("nickel", hx, yt, fz - 0.03, hx, yt, fz + 0.03, 0.42, 12, true)
		end
	end
	for _, rx in ipairs({-4.2, 0.0, 4.2}) do
		binPlenum:box("edge", rx, 33.72, PL_ZC, 0.28, 0.22, PL_ZH - 0.8)
	end
	binPlenum:box("duct_lamp", 0, 33.68, FAN_Z - 1.6, 8.4, 0.08, 0.20)
	binPlenum:box("duct_lamp", 0, 33.68, FAN_Z + 1.8, 8.4, 0.08, 0.20)

	-- Subtle internal tunnel PointLight so depth gleams visibly between spinning blades in Studio!
	local lightPart = Instance.new("Part")
	lightPart.Name = "TUNNEL_DEPTH_FILL_ANCHOR"
	lightPart.Size = Vector3.new(0.2, 0.2, 0.2)
	lightPart.Transparency = 1
	lightPart.Anchored = true; lightPart.CanCollide = false; lightPart.CanQuery = false; lightPart.CanTouch = false
	lightPart.CFrame = CFrame.new(toStudioPos(0, 21.5, FAN_Z))
	local pl = Instance.new("PointLight")
	pl.Color = Color3.fromRGB(190, 214, 248)
	pl.Brightness = 0.65
	pl.Range = 22
	pl.Shadows = false
	pl.Parent = lightPart

	local mPlenum = makeSubModel(staticRoot, "REACTOR_REAR_TURBINE_PLENUM_01")
	lightPart.Parent = mPlenum
	binPlenum:emitToModel(mPlenum, "PLENUM")

	local rotorCenterPart = Instance.new("Part")
	rotorCenterPart.Name = "ROTOR_HUB_PIVOT"
	rotorCenterPart.Size = Vector3.new(0.2, 0.2, 0.2)
	rotorCenterPart.Transparency = 1
	rotorCenterPart.Anchored = true; rotorCenterPart.CanCollide = false; rotorCenterPart.CanQuery = false; rotorCenterPart.CanTouch = false
	rotorCenterPart.CFrame = CFrame.new(rotorPivotStudio)
	rotorCenterPart.Parent = rotorModel
	rotorModel.PrimaryPart = rotorCenterPart
	binRotor:emitToModel(rotorModel, "TURBINE_ROTOR")
end

-- ============================================================================
-- 5. BUILD CROWN, PIT DECK, RADIATORS, TRUSSES, 4 RADIAL PORTS & 8 SLIDING LEAVES
-- ============================================================================
local radialHatches = {}
local contourLights = {}
do
	local binCrown = MeshBin.new()
	local Y_FRONT, Y_REAR = -18.0, 15.48
	local PORT_HOLE_X, PORT_HOLE_Y0, PORT_HOLE_Y1 = 6.20, -14.65, 9.25

	for _, pair in ipairs({{1, "ROOF"}, {-1, "DECK"}}) do
		local sgn = pair[1]
		local zIn, zMid = sgn * 21.50, sgn * 23.04
		for _, xr in ipairs({{-17.05, -PORT_HOLE_X}, {PORT_HOLE_X, 17.05}}) do
			local xc, xw = 0.5 * (xr[1] + xr[2]), xr[2] - xr[1]
			local yc, yw = 0.5 * (Y_FRONT + Y_REAR), Y_REAR - Y_FRONT
			-- gunmetal starts at |Z_src|=21.82 while iron liner occupies 21.51..21.75 (%0 coplanar Z-fight!)
			binCrown:box("gunmetal", xc, yc, zMid, xw, yw, 2.44)
			binCrown:box("iron", xc, yc, zIn + sgn * 0.13, xw - 0.22, yw - 0.28, 0.24)
		end
		for _, yr in ipairs({{Y_FRONT, PORT_HOLE_Y0}, {PORT_HOLE_Y1, Y_REAR}}) do
			local yc, yw = 0.5 * (yr[1] + yr[2]), yr[2] - yr[1]
			binCrown:box("gunmetal", 0, yc, zMid, PORT_HOLE_X * 2, yw, 2.44)
			binCrown:box("iron", 0, yc, zIn + sgn * 0.13, PORT_HOLE_X * 2 - 0.18, yw - 0.18, 0.24)
		end
		for _, yRib in ipairs({-16.8, -14.8, 9.5, 13.8}) do
			binCrown:box("frame", 0, yRib, zIn - sgn * 0.26, 33.8, 0.62, 0.44)
			binCrown:cyl("edge", -16.8, yRib, zIn - sgn * 0.52, 16.8, yRib, zIn - sgn * 0.52, 0.075, 8, false)
		end
		for _, yL in ipairs({-15.4, 10.6}) do
			binCrown:box("frame", 0, yL, zIn - sgn * 0.10, 32.8, 0.42, 0.14)
			binCrown:box("lumen", 0, yL, zIn - sgn * 0.21, 32.2, 0.13, 0.06)
			for _, side in ipairs({-1, 1}) do
				binCrown:cyl("frame", side * 16.4, yL, sgn * 21.30, side * 23.1, yL, sgn * 13.55, 0.16, 8, false)
				binCrown:cyl("lumen", side * 16.26, yL - 0.06, sgn * 21.18, side * 22.96, yL - 0.06, sgn * 13.43, 0.065, 8, false)
			end
		end
	end

	-- 4 Open-Through Radial Port Housings + 8 Separately Grouped Sliding Hatch Leaves
	local function addRadialPort(tag, codeTxt, outDir, radiusSeat, bayHalfW)
		local d = outDir.Unit
		local inward = -d
		local yAx = Vector3.yAxis -- authoring +Y = (0, 1, 0)
		local zAx = inward:Cross(yAx).Unit
		local center = Vector3.new(0, -2.70, 0) + d * radiusSeat
		local R = CFrame.fromMatrix(center, inward, yAx, zAx)
		local function lp(lx, ly, lz)
			local w = R:PointToWorldSpace(Vector3.new(lx, ly, lz))
			return w.X, w.Y, w.Z
		end
		local function pBox(bin, mKey, lx, ly, lz, sx, sy, sz)
			local wx, wy, wz = lp(lx, ly, lz)
			bin:box(mKey, wx, wy, wz, sx, sy, sz, R.Rotation)
		end

		local apY, apZ = 4.15, 4.15
		-- Exact flush fit inside PORT_HOLE (11.95 x 6.20) so inner port housing NEVER overlaps CROWN/DECK iron liner!
		local frY, frZ = 11.90, bayHalfW
		local sideW = math.max(0.75, frZ - apZ)

		pBox(binCrown, "gunmetal", -0.25, -(apY + (frY - apY) * 0.5), 0, 3.10, frY - apY, frZ * 2)
		pBox(binCrown, "gunmetal", -0.25,  (apY + (frY - apY) * 0.5), 0, 3.10, frY - apY, frZ * 2)
		pBox(binCrown, "gunmetal", -0.25, 0, -(apZ + sideW * 0.5), 3.10, apY * 2, sideW)
		pBox(binCrown, "gunmetal", -0.25, 0,  (apZ + sideW * 0.5), 3.10, apY * 2, sideW)

		-- Exterior-only overlapping seal collar (strictly outside |Z_src|=24.26 / r=27.80 -> %0 skybox & %0 Z-fight!)
		local extFrY, extFrZ = frY + 0.85, frZ + 0.85
		local extLx = -3.02
		pBox(binCrown, "gunmetal", extLx, -(apY + (extFrY - apY) * 0.5), 0, 0.88, extFrY - apY, extFrZ * 2)
		pBox(binCrown, "gunmetal", extLx,  (apY + (extFrY - apY) * 0.5), 0, 0.88, extFrY - apY, extFrZ * 2)
		pBox(binCrown, "gunmetal", extLx, 0, -(apZ + (extFrZ - apZ) * 0.5), 0.88, apY * 2, extFrZ - apZ)
		pBox(binCrown, "gunmetal", extLx, 0,  (apZ + (extFrZ - apZ) * 0.5), 0.88, apY * 2, extFrZ - apZ)

		local shL = 5.4
		pBox(binCrown, "dark", -1.85 - shL * 0.5, -apY - 0.22, 0, shL, 0.40, apZ * 2 + 0.80)
		pBox(binCrown, "dark", -1.85 - shL * 0.5,  apY + 0.22, 0, shL, 0.40, apZ * 2 + 0.80)
		pBox(binCrown, "dark", -1.85 - shL * 0.5, 0, -apZ - 0.22, shL, apY * 2, 0.40)
		pBox(binCrown, "dark", -1.85 - shL * 0.5, 0,  apZ + 0.22, shL, apY * 2, 0.40)

		pBox(binCrown, "edge", 1.44, -apY - 0.18, 0, 0.24, 0.36, apZ * 2 + 0.72)
		pBox(binCrown, "edge", 1.44,  apY + 0.18, 0, 0.24, 0.36, apZ * 2 + 0.72)
		pBox(binCrown, "edge", 1.44, 0, -apZ - 0.18, 0.24, apY * 2, 0.36)
		pBox(binCrown, "edge", 1.44, 0,  apZ + 0.18, 0.24, apY * 2, 0.36)

		-- Stepped forward cleanly proud of gunmetal front face (lx = 1.30): dark at 1.33..1.41, hazard at 1.44..1.48!
		for _, sgnZ in ipairs({-1, 1}) do
			local zH = sgnZ * (frZ - 0.52)
			pBox(binCrown, "dark", 1.37, 0, zH, 0.08, 15.2, 0.78)
			local sy = -6.8
			while sy <= 6.2 do
				local p1x, p1y, p1z = lp(1.45, sy, zH - 0.32)
				local p2x, p2y, p2z = lp(1.45, sy + 0.65, zH - 0.32)
				local p3x, p3y, p3z = lp(1.45, sy + 1.05, zH + 0.32)
				local p4x, p4y, p4z = lp(1.45, sy + 0.40, zH + 0.32)
				binCrown:quad("hazard", {{p1x, p1y, p1z}, {p2x, p2y, p2z}, {p3x, p3y, p3z}, {p4x, p4y, p4z}})
				sy += 1.35
			end
		end

		for _, sgnZ in ipairs({-1, 1}) do
			pBox(binCrown, "frame", 0.92, 0, sgnZ * (apZ + 0.42), 0.45, 22.8, 0.42)
		end

		-- Equipment plaque cleanly proud of gunmetal (1.33..1.43) + SurfaceGui at 1.47 (%0 Z-fight!)
		local nIn = toStudioVec(inward.X, inward.Y, inward.Z).Unit
		local isHorizPlate = math.abs(nIn.Y) > 0.95
		if isHorizPlate then
			pBox(binCrown, "sign", 1.38, -7.85, 0, 0.10, 2.2, 4.4)
		else
			pBox(binCrown, "sign", 1.38, -7.85, 0, 0.10, 4.4, 2.2)
		end
		do
			local pw = R:PointToWorldSpace(Vector3.new(1.47, -7.85, 0))
			local pSt = toStudioPos(pw.X, pw.Y, pw.Z)
			local upHint
			if isHorizPlate then
				upHint = (nIn.Y > 0) and Vector3.new(0, 0, -1) or Vector3.new(0, 0, 1)
			else
				upHint = Vector3.yAxis
			end
			local signPart = Instance.new("Part")
			signPart.Name = "PLAQUE_" .. codeTxt
			signPart.Size = Vector3.new(4.1, 2.0, 0.04)
			signPart.Transparency = 1
			signPart.Anchored = true; signPart.CanCollide = false; signPart.CanQuery = false; signPart.CanTouch = false
			signPart.CFrame = CFrame.lookAt(pSt, pSt + nIn, upHint)
			signPart:SetAttribute("Faz2Generated", true)
			local sgui = Instance.new("SurfaceGui")
			sgui.Face = Enum.NormalId.Front
			sgui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
			sgui.PixelsPerStud = 48
			sgui.LightInfluence = 0.72
			sgui.Brightness = 0.65
			sgui.Parent = signPart
			local lbl = Instance.new("TextLabel")
			lbl.Size = UDim2.new(0.88, 0, 0.56, 0)
			lbl.Position = UDim2.new(0.06, 0, 0.22, 0)
			lbl.BackgroundTransparency = 1
			lbl.Font = Enum.Font.Code
			lbl.Text = codeTxt
			lbl.TextColor3 = Color3.fromRGB(218, 226, 236)
			lbl.TextScaled = true
			lbl.Parent = sgui
			signPart.Parent = staticRoot
		end

		local mHatch = makeSubModel(movingRoot, "REACTOR_RADIAL_HATCH_" .. tag)
		local mLeft = makeSubModel(mHatch, "LEAF_LEFT")
		local mRight = makeSubModel(mHatch, "LEAF_RIGHT")
		for _, lf in ipairs({{-1, mLeft}, {1, mRight}}) do
			local sgnY, leafModel = lf[1], lf[2]
			local binLeaf = MeshBin.new()
			local yc = sgnY * (apY * 0.5 + 0.04)
			local yh = apY + 0.06
			pBox(binLeaf, "plate", 0.72, yc, 0, 0.40, yh, apZ * 2 + 0.24)
			for _, rz in ipairs({-2.5, 0.0, 2.5}) do
				pBox(binLeaf, "frame", 1.00, yc, rz, 0.12, yh - 0.42, 0.34)
			end
			local seamY = -sgnY * (yh * 0.5 - 0.14)
			pBox(binLeaf, "edge", 1.02, yc + seamY, 0, 0.14, 0.24, apZ * 2 + 0.16)
			binLeaf:emitToModel(leafModel, "HATCH_" .. (sgnY < 0 and "LEFT" or "RIGHT"))
		end
		radialHatches[#radialHatches + 1] = {
			tag = tag,
			left = mLeft, leftHome = mLeft:GetPivot(),
			right = mRight, rightHome = mRight:GetPivot(),
		}
	end

	addRadialPort("UPPER",       "SL-00", Vector3.new(0, 0, 1),          21.75, 6.16)
	addRadialPort("LOWER",       "SL-05", Vector3.new(0, 0, -1),         21.75, 6.16)
	addRadialPort("LOWER_LEFT",  "SL-03", Vector3.new(-0.72, 0, -0.694), 26.10, 5.12)
	addRadialPort("LOWER_RIGHT", "SL-04", Vector3.new( 0.72, 0, -0.694), 26.10, 5.12)

	-- Rear Exterior Seam Backing Shroud pushed cleanly back to Y_src = +18.60 (100% behind REV05 & Faz3 exhaust hoods!)
	binCrown:box("gunmetal", -18.20, 18.60,  1.80, 22.00, 0.70, 50.00)
	binCrown:box("gunmetal",  18.20, 18.60,  1.80, 22.00, 0.70, 50.00)
	binCrown:box("gunmetal",   0.00, 18.60, 22.20, 15.00, 0.70,  9.20)
	binCrown:box("gunmetal",   0.00, 18.60,-15.80, 15.00, 0.70, 17.20)
	-- Exterior-only rear octagonal corner sleeves (nOut = +3.35 -> 100% outside REV02 & CROWN_DECK!)
	for _, sxR in ipairs({-1, 1}) do
		for _, szR in ipairs({-1, 1}) do
			local x0, z0 = sxR * 24.50, szR * 12.50
			local x1, z1 = sxR * 17.00, szR * 21.50
			local cx, cz = 0.5 * (x0 + x1), 0.5 * (z0 + z1)
			local bLen = math.sqrt((x1 - x0)^2 + (z1 - z0)^2) + 2.40
			local nOut = Vector3.new(sxR * 0.7682, 0, szR * 0.6402).Unit
			local rotR = CFrame.fromMatrix(Vector3.zero, nOut, Vector3.yAxis, nOut:Cross(Vector3.yAxis).Unit)
			local pM = Vector3.new(cx, 15.60, cz) + nOut * 3.45
			binCrown:box("gunmetal", pM.X, pM.Y, pM.Z, 1.15, 6.60, bLen, rotR)
		end
		binCrown:box("gunmetal", sxR * 28.55, 15.60, 0.0, 1.25, 6.60, 28.00)
	end
	binCrown:box("gunmetal", 0, 16.20,  24.95, 38.00, 5.20, 1.20)
	binCrown:box("gunmetal", 0, 16.20, -24.95, 38.00, 5.20, 1.20)

	for _, side in ipairs({-1, 1}) do
		for _, yg in ipairs({-14.55, 9.15}) do
			binCrown:cyl("frame", side * 23.95, yg, -12.6, side * 16.95, yg, -21.35, 0.20, 10, false)
		end
		-- Olive-taupe louvered radiator banks (every layer stepped cleanly forward of 12.925 -> %0 Z-fight!)
		local xc, yc, zc = side * 12.6, 13.55, -14.8
		binCrown:box("gunmetal", xc, yc, zc, 11.2, 1.25, 6.4)
		binCrown:box("dark", xc, yc - 0.70, zc - 0.25, 10.2, 0.12, 4.6)
		for li = 0, 21 do
			local lx = (xc - 4.7) + 9.4 * (li / 21)
			binCrown:box("radiator", lx, yc - 0.81, zc - 0.25, 0.24, 0.14, 4.35)
		end
		binCrown:box("dark", xc, yc - 0.70, zc + 2.55, 10.8, 0.12, 0.44)
		for hi = 0, 13 do
			local hx = (xc - 5.0) + 9.5 * (hi / 13)
			binCrown:quad("caution", {
				{hx, yc - 0.80, zc + 2.36}, {hx + 0.36, yc - 0.80, zc + 2.36},
				{hx + 0.60, yc - 0.80, zc + 2.74}, {hx + 0.24, yc - 0.80, zc + 2.74},
			})
		end
		binCrown:box("dark", xc, yc - 0.72, -20.85, 10.8, 0.14, 0.78)
		for si = 0, 7 do
			local sx = (xc - 4.8) + 9.0 * (si / 7)
			binCrown:quad("hazard", {
				{sx, yc - 0.83, -21.20}, {sx + 0.56, yc - 0.83, -21.20},
				{sx + 0.92, yc - 0.83, -20.52}, {sx + 0.36, yc - 0.83, -20.52},
			})
		end

		-- Inner & Outer Open-Web Corner Trusses + Upper & Lower Strip Worklights
		local xIn, yIn = side * 6.45, 14.35
		for _, dx in ipairs({-0.32, 0.32}) do
			binCrown:cyl("frame", xIn + dx, yIn, -11.5, xIn + dx, yIn, 16.5, 0.11, 8, false)
		end
		local zs = -11.0
		while zs < 15.7 do
			binCrown:cyl("edge", xIn - 0.32, yIn - 0.05, zs, xIn + 0.32, yIn - 0.05, zs + 0.92, 0.055, 6, false)
			binCrown:cyl("edge", xIn + 0.32, yIn - 0.05, zs + 0.92, xIn - 0.32, yIn - 0.05, zs + 1.85, 0.055, 6, false)
			zs += 1.85
		end
		for _, wl in ipairs({{11.6, 5.4}, {-3.6, 4.6}}) do
			binCrown:box("frame", xIn, yIn - 0.22, wl[1], 0.52, 0.26, wl[2])
			binCrown:box("worklight", xIn, yIn - 0.36, wl[1], 0.28, 0.08, wl[2] - 0.45)
		end

		local xOut, yOut = side * 18.25, 11.85
		for _, dx in ipairs({-0.34, 0.34}) do
			binCrown:cyl("frame", xOut + dx * 0.7, yOut + dx * 0.7, -12.0, xOut + dx * 0.7, yOut + dx * 0.7, 12.6, 0.12, 8, false)
		end
		local zo = -11.5
		while zo < 11.7 do
			binCrown:cyl("edge", xOut - 0.24, yOut - 0.24, zo, xOut + 0.24, yOut + 0.24, zo + 1.0, 0.06, 6, false)
			binCrown:cyl("edge", xOut + 0.24, yOut + 0.24, zo + 1.0, xOut - 0.24, yOut - 0.24, zo + 2.0, 0.06, 6, false)
			zo += 2.0
		end
	end

	local mCrown = makeSubModel(staticRoot, "REACTOR_CROWN_AND_DECK_01")
	-- Balanced, non-bleaching architectural contour & worklight illumination inside the sealed octagonal chamber
	local fillSpecs = {
		{pos = toStudioPos(-12.5, -1.5,  17.5), br = 0.62, rng = 40, col = Color3.fromRGB(214, 225, 240)},
		{pos = toStudioPos( 12.5, -1.5,  17.5), br = 0.62, rng = 40, col = Color3.fromRGB(214, 225, 240)},
		{pos = toStudioPos(-12.5,  5.5, -15.0), br = 0.52, rng = 36, col = Color3.fromRGB(210, 220, 234)},
		{pos = toStudioPos( 12.5,  5.5, -15.0), br = 0.52, rng = 36, col = Color3.fromRGB(210, 220, 234)},
		{pos = toStudioPos(  0.0, -9.5,   4.0), br = 0.58, rng = 44, col = Color3.fromRGB(216, 226, 240)},
		{pos = toStudioPos(  0.0, 12.2,   2.2), br = 0.55, rng = 26, col = Color3.fromRGB(214, 225, 240)},
	}
	for idx, fs in ipairs(fillSpecs) do
		local lp = Instance.new("Part")
		lp.Name = "CHAMBER_CONTOUR_FILL_" .. idx
		lp.Size = Vector3.new(0.2, 0.2, 0.2)
		lp.Transparency = 1
		lp.Anchored = true; lp.CanCollide = false; lp.CanQuery = false; lp.CanTouch = false
		lp.CFrame = CFrame.new(fs.pos)
		local pt = Instance.new("PointLight")
		pt.Color = fs.col
		pt.Brightness = fs.br
		pt.Range = fs.rng
		pt.Shadows = false
		pt.Parent = lp
		lp.Parent = mCrown
		contourLights[#contourLights + 1] = {light = pt, baseBr = fs.br}
	end
	binCrown:emitToModel(mCrown, "CROWN_DECK")
end

-- ============================================================================
-- 6. OPEN-PORT LOWER DIAGONAL SIDE WALLS + FRONT OCTAGONAL BULKHEAD SEAL
-- ============================================================================
do
	local binDiag = MeshBin.new()
	local function rearYx(ax)
		local t = math.clamp((ax - 16.14) / (24.5 - 16.14), 0, 1)
		return 15.48 - 2.55 * t * t * (3 - 2 * t)
	end
	local function warpC(y, z)
		local zt = math.clamp((math.abs(z) - 12.5) / 9.0, 0, 1)
		local bx = 24.5 - 7.5 * zt
		local y0 = rearYx(bx)
		local t = math.clamp((y - 9.7) / (y0 - 9.7), 0, 1)
		local sm = t * t * (3 - 2 * t)
		local ins = bx - 3.30 * (1 - zt) * sm
		return ins, y + sm * (rearYx(ins) - y0)
	end
	local function frontYz(z)
		return -18.0 + 2.35 * math.clamp((math.abs(z) - 12.5) / 9.0, 0, 1)
	end
	local function rearYz(z)
		local t = math.clamp((math.abs(z) - 12.5) / 9.0, 0, 1)
		return rearYx(24.5 - 7.5 * t)
	end

	local yGrid = {-18.0, -14.70, -8.55, 3.15, 9.30, 11.5, 13.5, 15.48}
	local zGrid = {-21.45, -21.15, -19.0, -16.5, -14.25, -13.4, -12.55}
	for _, side in ipairs({-1, 1}) do
		for _, spec in ipairs({{"frame", 0.0, 3.22}, {"iron_lower", 0.41, -0.105}}) do
			local mKey, fPush, bPush = spec[1], spec[2], spec[3]
			local vs, fidx, bidx, fs, backOf, frontTris = {}, {}, {}, {}, {}, {}
			local function gv(yv, zv, back)
				local k = string.format("%.3f_%.3f", yv, zv)
				local D = back and bidx or fidx
				if not D[k] then
					local yc = math.clamp(yv, frontYz(zv), rearYz(zv))
					local mag, ry = warpC(yc, zv)
					local x = side * (mag + (back and bPush or -fPush))
					local id = #vs + 1
					vs[id] = {x, ry, zv}
					D[k] = id
				end
				return D[k]
			end
			for yi = 1, #yGrid - 1 do
				local ya, yb = yGrid[yi], yGrid[yi + 1]
				for zi = 1, #zGrid - 1 do
					local za, zb = zGrid[zi], zGrid[zi + 1]
					local yc, zc = 0.5 * (ya + yb), 0.5 * (za + zb)
					local inHole = (yc >= -8.55 and yc <= 3.15) and (zc >= -21.15 and zc <= -14.25)
					if not inHole and yb > frontYz(zc) + 0.05 and ya < rearYz(zc) - 0.05 then
						local a, b, c, d = gv(ya, za, false), gv(yb, za, false), gv(yb, zb, false), gv(ya, zb, false)
						local A, B, C, D = gv(ya, za, true),  gv(yb, za, true),  gv(yb, zb, true),  gv(ya, zb, true)
						backOf[a] = A; backOf[b] = B; backOf[c] = C; backOf[d] = D
						if side < 0 then
							frontTris[#frontTris + 1] = {a, b, c}; frontTris[#frontTris + 1] = {a, c, d}
							fs[#fs + 1] = {a, b, c}; fs[#fs + 1] = {a, c, d}
							fs[#fs + 1] = {A, C, B}; fs[#fs + 1] = {A, D, C}
						else
							frontTris[#frontTris + 1] = {a, c, b}; frontTris[#frontTris + 1] = {a, d, c}
							fs[#fs + 1] = {a, c, b}; fs[#fs + 1] = {a, d, c}
							fs[#fs + 1] = {A, B, C}; fs[#fs + 1] = {A, C, D}
						end
					end
				end
			end
			local eUses = {}
			for _, t in ipairs(frontTris) do
				for _, pr in ipairs({{t[1], t[2]}, {t[2], t[3]}, {t[3], t[1]}}) do
					local u, v = pr[1], pr[2]
					local k = u < v and (u .. "_" .. v) or (v .. "_" .. u)
					if not eUses[k] then eUses[k] = {} end
					table.insert(eUses[k], pr)
				end
			end
			for _, uses in pairs(eUses) do
				if #uses == 1 then
					local u, v = uses[1][1], uses[1][2]
					local U, V = backOf[u], backOf[v]
					fs[#fs + 1] = {u, V, v}; fs[#fs + 1] = {u, U, V}
				end
			end
			binDiag:addRaw(mKey, vs, fs, false, 12.0)
		end
	end

	-- Front Octagonal Bulkhead Seal cleanly in front of REV02 (+18.12) & CROWN_DECK (+18.00):
	-- Spans Y_src = -19.80 .. -18.30 (Studio Z = +18.30 .. +19.80) -> %0 overlap with REV02 gussets!
	binDiag:box("gunmetal", -60.25, -19.05, 28.5, 71.5, 1.50, 112.0)
	binDiag:box("gunmetal",  60.25, -19.05, 28.5, 71.5, 1.50, 112.0)
	binDiag:box("gunmetal", 0, -19.05,  52.5, 49.00, 1.50, 62.00)
	binDiag:box("gunmetal", 0, -19.05, -24.5, 49.00, 1.50,  6.00)

	-- Exterior-Only Throat Collar Sleeves bridging Y_src = -18.45 .. -15.00 STRICTLY OUTSIDE REV02 (27.72) & CROWN_DECK (24.26)!
	binDiag:box("gunmetal", 0, -16.80,  24.95, 38.00, 3.60, 1.20)
	binDiag:box("gunmetal", 0, -16.80, -24.95, 38.00, 3.60, 1.20)
	for _, sx in ipairs({-1, 1}) do
		binDiag:box("gunmetal", sx * 28.55, -16.80, 0.0, 1.25, 3.60, 28.00)
	end

	-- 4 Exterior-Only 45° Octagonal Chamfer Sleeves (nOut = +3.45 -> 100% OUTSIDE REV02 front corner gussets!)
	for _, sx in ipairs({-1, 1}) do
		for _, sz in ipairs({-1, 1}) do
			local x0, z0 = sx * 24.50, sz * 12.50
			local x1, z1 = sx * 17.00, sz * 21.50
			local cx, cz = 0.5 * (x0 + x1), 0.5 * (z0 + z1)
			local bevelLen = math.sqrt((x1 - x0)^2 + (z1 - z0)^2) + 2.40
			local nOut = Vector3.new(sx * 0.7682, 0, sz * 0.6402).Unit
			local yFwd = Vector3.new(0, 1, 0)
			local tBev = nOut:Cross(yFwd).Unit
			local rotBev = CFrame.fromMatrix(Vector3.zero, nOut, yFwd, tBev)
			local pMid = Vector3.new(cx, -16.85, cz) + nOut * 3.45
			binDiag:box("gunmetal", pMid.X, pMid.Y, pMid.Z, 1.15, 4.10, bevelLen, rotBev)

			-- Front 45° Corner Gusset Wedges at Y_src = -19.78 .. -18.32 (100% single-sided outward-facing normals!)
			local vsW = {}
			for _, yv in ipairs({-19.78, -18.32}) do
				vsW[#vsW + 1] = {sx * 24.48, yv, sz * 12.48}
				vsW[#vsW + 1] = {sx * 24.48, yv, sz * 21.52}
				vsW[#vsW + 1] = {sx * 16.98, yv, sz * 21.52}
			end
			local cW = Vector3.zero
			for i = 1, 6 do cW += toStudioPos(vsW[i][1], vsW[i][2], vsW[i][3]) end
			cW /= 6
			local fsBase = {
				{1, 2, 3}, {4, 6, 5},
				{1, 4, 5}, {1, 5, 2},
				{2, 5, 6}, {2, 6, 3},
				{3, 6, 4}, {3, 4, 1},
			}
			local fsOut = {}
			for _, tr in ipairs(fsBase) do
				local s1 = toStudioPos(vsW[tr[1]][1], vsW[tr[1]][2], vsW[tr[1]][3])
				local s2 = toStudioPos(vsW[tr[2]][1], vsW[tr[2]][2], vsW[tr[2]][3])
				local s3 = toStudioPos(vsW[tr[3]][1], vsW[tr[3]][2], vsW[tr[3]][3])
				local fn = (s2 - s1):Cross(s3 - s1)
				local fc = (s1 + s2 + s3) / 3
				if fn:Dot(fc - cW) >= 0 then
					fsOut[#fsOut + 1] = {tr[1], tr[2], tr[3]}
				else
					fsOut[#fsOut + 1] = {tr[1], tr[3], tr[2]}
				end
			end
			binDiag:addRaw("frame", vsW, fsOut, true, 12.0)
		end
	end
	local octP = {{-17, -21.5}, {17, -21.5}, {24.5, -12.5}, {24.5, 12.5}, {17, 21.5}, {-17, 21.5}, {-24.5, 12.5}, {-24.5, -12.5}}
	for i = 1, #octP do
		local a, b = octP[i], octP[(i % #octP) + 1]
		binDiag:cyl("edge", a[1], -18.55, a[2], b[1], -18.55, b[2], 0.24, 8, true)
	end

	local mSeal = makeSubModel(staticRoot, "REACTOR_SIDE_DIAG_OPEN_AND_FRONT_SEAL_03")
	binDiag:emitToModel(mSeal, "OCTAGON_SEAL")
end

-- ============================================================================
-- 7. NON-DESTRUCTIVE PALETTE UPGRADE OF EXISTING REV02 / REV04 / GRILLES / HATCHES
--    + SYMMETRIC 3-PANE CONTROL-ROOM MULLIONS (01_komut_110.jpg)
-- ============================================================================
local COLOR_UPPER_SLATE  = Color3.fromRGB(101, 113, 134)
local COLOR_MID_GRAPHITE = Color3.fromRGB( 74,  79,  94)
local COLOR_DADO_OLIVE   = Color3.fromRGB( 72,  69,  61)

local function replaceSurfaceColor(mp, col, refl)
	for _, ch in ipairs(mp:GetChildren()) do
		if ch:IsA("SurfaceAppearance") then ch:Destroy() end
	end
	pcall(function() mp.TextureID = "" end)
	mp.Color = col
	mp.Material = Enum.Material.Metal
	mp.Reflectance = refl or 0.03
end

local oldRev04 = staticRoot:FindFirstChild("REACTOR_REAR_BULKHEAD_IRON_REV04")
if oldRev04 then
	for _, d in ipairs(oldRev04:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Transparency = 1
			d.CanQuery = false
			d.CanCollide = false
		end
	end
end

local sideRev02 = staticRoot:FindFirstChild("REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02")
if sideRev02 then
	for _, d in ipairs(sideRev02:GetDescendants()) do
		if d:IsA("MeshPart") then
			local n = d.Name
			if n:find("LOWER_DIAGONAL_STRUCTURAL_BLOCK", 1, true) or n:find("LOWER_SLOPED_ROLLED_IRON", 1, true) then
				d.Transparency = 1
				d.CanQuery = false
				d.CanCollide = false
			elseif n:find("UPPER_SLOPED_ROLLED_IRON", 1, true) or n:find("STAMPED_WAIST_COURSE_3", 1, true) then
				replaceSurfaceColor(d, COLOR_UPPER_SLATE, 0.04)
			elseif n:find("STAMPED_WAIST_COURSE_2", 1, true) then
				replaceSurfaceColor(d, COLOR_MID_GRAPHITE, 0.03)
			elseif n:find("STAMPED_WAIST_COURSE_1", 1, true) then
				replaceSurfaceColor(d, COLOR_DADO_OLIVE, 0.02)
			elseif n:find("__liner", 1, true) or n:find("__frame", 1, true) then
				replaceSurfaceColor(d, Color3.fromRGB(44, 48, 56), 0.03)
			end
		end
	end
end

local rearGrilles = staticRoot:FindFirstChild("REACTOR_REAR_SERVICE_GRILLES_01")
if rearGrilles then
	for _, d in ipairs(rearGrilles:GetDescendants()) do
		if d:IsA("MeshPart") then
			local n = d.Name
			if n:find("__wall", 1, true) or n:find("__paint", 1, true) then
				replaceSurfaceColor(d, COLOR_UPPER_SLATE, 0.04)
			elseif n:find("__copper", 1, true) or n:find("__seal", 1, true) then
				replaceSurfaceColor(d, Color3.fromRGB(88, 96, 110), 0.05)
			elseif n:find("__amber", 1, true) then
				replaceSurfaceColor(d, Color3.fromRGB(190, 168, 58), 0.0)
				d.Material = Enum.Material.SmoothPlastic
			end
		end
	end
end

for _, hTag in ipairs({"LEFT", "RIGHT"}) do
	local hModel = movingRoot:FindFirstChild("REACTOR_WALL_HATCH_THROUGH_01_" .. hTag)
	if hModel then
		local sgnX = (hTag == "RIGHT") and 1 or -1
		local inwardStep = {
			WARNING_BAND__dark     = 0.035, -- 24.470 -> 24.435 (0.045 clear of INSET_SHEET__panel 24.480)
			WARNING_PAINT__hazard  = 0.068, -- 24.455 -> 24.387 (0.048 clear of WARNING_BAND__dark)
			EQUIPMENT_LABEL__label = 0.125, -- 24.468 -> 24.343 (0.044 proud of WARNING_PAINT__hazard)
			HATCH_LEFT__panel      = 0.045, -- 24.255 -> 24.210 (eliminates 0.0000 coplanar clash with HATCH_LEFT__edge!)
			HATCH_RIGHT__panel     = 0.045, -- 24.255 -> 24.210 (eliminates 0.0000 coplanar clash with HATCH_RIGHT__edge!)
			HATCH_LEFT__hazard     = 0.070, -- 24.233 -> 24.163 (0.047 clear of HATCH_LEFT__panel)
			HATCH_RIGHT__hazard    = 0.070, -- 24.233 -> 24.163 (0.047 clear of HATCH_RIGHT__panel)
		}
		for _, d in ipairs(hModel:GetDescendants()) do
			if d:IsA("MeshPart") then
				local n = d.Name
				if n == "FACILITY_SHEET__upper" then
					replaceSurfaceColor(d, COLOR_UPPER_SLATE, 0.04)
				elseif n:find("__hazard", 1, true) then
					replaceSurfaceColor(d, Color3.fromRGB(206, 210, 216), 0.0)
					d.Material = Enum.Material.SmoothPlastic
				end
				local step = inwardStep[n]
				if step then
					local origX = d:GetAttribute("OrigPosX")
					if typeof(origX) ~= "number" then
						origX = d.Position.X
						d:SetAttribute("OrigPosX", origX)
					end
					local p = d.Position
					d.CFrame = d.CFrame.Rotation + Vector3.new(origX - sgnX * step, p.Y, p.Z)
				end
			end
		end
	end
end

-- Upgrade Control Room glass mullion to symmetric 3-pane mullions (X = +/-22.5) + hide floating R5 ceiling balls
if world then
	local containment = world:FindFirstChild("01_CONTAINMENT")
	if containment then
		for _, p in ipairs(containment:GetChildren()) do
			if p:IsA("BasePart") and (p.Name == "CAMBER_BEAM_LAMP" or p.Name == "CHAMBER_CEILING_SERVICE_RAIL") then
				p.Transparency = 1
				for _, l in ipairs(p:GetChildren()) do
					if l:IsA("Light") then l.Enabled = false end
				end
			end
		end
	end
	local gallery = world:FindFirstChild("02_PANORAMIC_CONTROL_ROOM")
	if gallery then
		local oldMullion = gallery:FindFirstChild("SLIM_OFFSET_GLASS_MULLION")
		if oldMullion and oldMullion:IsA("BasePart") then
			-- Real-stud coordinates (CORE_PROTOCOL_Server uses WORLD_SCALE = 0.50 -> glass at Z = 46.625, Y = 24.625)
			oldMullion.Position = Vector3.new(-11.25, 24.625, 46.725)
			oldMullion.Size = Vector3.new(0.42, 22.5, 0.65)
			oldMullion.Color = Color3.fromRGB(38, 42, 50)
			local rightMullion = gallery:FindFirstChild("SLIM_SYMMETRIC_GLASS_MULLION_R")
			if not rightMullion then
				rightMullion = oldMullion:Clone()
				rightMullion.Name = "SLIM_SYMMETRIC_GLASS_MULLION_R"
				rightMullion.Position = Vector3.new(11.25, 24.625, 46.725)
				rightMullion.Parent = gallery
			end
		end
	end
end

-- ============================================================================
-- 8. LIVE 60 HZ MECHANICAL DRIVER: 4 RADIAL SLIDING HATCHES + 10-BLADE TURBINE!
-- ============================================================================
local function glide(t)
	t = math.clamp(t, 0, 1)
	return t * t * (3 - 2 * t)
end

local rotorAngle = 0.0
local rotorSpeedDeg = 22.0 -- gentle idle draft in COLD

if RunService:IsRunning() then
	RunService.Heartbeat:Connect(function(dt)
		dt = math.min(dt, 0.1)
		local mode = world and world:GetAttribute("ReactorMode") or "COLD"
		local isStartup = (mode == "STARTUP")

		-- 1) Synchronize all 4 new radial dual-leaf sliding hatches (SL-00, SL-03, SL-04, SL-05)
		for _, h in ipairs(radialHatches) do
			local rawG = isStartup
				and (assembly:GetAttribute("ReactorPilotGate_" .. h.tag) or 0)
				or  (assembly:GetAttribute("LiveGate_" .. h.tag) or 0)
			local slide = 5.85 * glide(rawG)
			-- Authoring +Y maps to Studio -Z: LEAF_LEFT (-5.85 Y_src -> +5.85 Z_studio), LEAF_RIGHT (+5.85 Y_src -> -5.85 Z_studio)
			h.left:PivotTo(CFrame.new(0, 0, slide) * h.leftHome)
			h.right:PivotTo(CFrame.new(0, 0, -slide) * h.rightHome)
		end

		-- 2) Smoothly spin 10-Blade Rear Turbine Rotor around Studio Z axis at (0, 28.30, -16.25)!
		local targetDeg = 22.0
		if mode == "STARTUP" then
			local age = world and world:GetAttribute("ReactorStartupAge") or 0
			targetDeg = 22.0 + 148.0 * glide((age - 2.0) / 18.0)
		elseif mode == "ONLINE" or mode == "WARNING" then
			targetDeg = 170.0
		elseif mode == "MELTDOWN" then
			targetDeg = 240.0
		elseif mode == "FREEZEDOWN" or mode == "AFTERMATH" then
			targetDeg = 8.0
		end
		rotorSpeedDeg += (targetDeg - rotorSpeedDeg) * math.min(1, dt * 1.8)
		rotorAngle = (rotorAngle + math.rad(rotorSpeedDeg) * dt) % (math.pi * 2)
		rotorModel:PivotTo(CFrame.new(rotorPivotStudio) * CFrame.Angles(0, 0, rotorAngle))
		-- 3) Modulate chamber contour lights smoothly with ReactorPilotDarkness (bright in COLD & ONLINE, dimmed in Stage 03-04 dark hold!)
		local darkness = (isStartup and world and world:GetAttribute("ReactorPilotDarkness")) or 0
		local dimScale = math.clamp(1.0 - 0.78 * darkness, 0.22, 1.0)
		for _, cl in ipairs(contourLights) do
			cl.light.Brightness = cl.baseBr * dimScale
		end
	end)
end

assembly:SetAttribute("Faz2ChamberMounted", true)
assembly:SetAttribute("RearTurbineBlades", 10)
print("[FAZ2] Multi-tone Slate-Iron Chamber, 4 Radial Sliding Hatches & 10-Blade CNC Rear Turbine active!")
