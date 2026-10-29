--!nonstrict
-- ============================================================================
-- FAZ 4.2 — DAMAGE_PIPE_RUPTURE_KIT_01 (M13)
-- 4 adet PIPE_SPOOL modülünün RUPTURED (patlamış) karşılıkları: gerçek içi
-- delik yırtık güdükler (dikiş patlaması + dişli ağız + et kalınlığı), aynı
-- uç/flanş düzlemleri, yarık kriyo bantlar, kıvrık metal parçacıklar ve
-- hacimsel sızıntı hunisi için ağız ankrajları (MOUTH_A / MOUTH_B).
-- Parçalar GIZLI dogar (Transparency=1); degisim mekanigi INTACT gizle <->
-- RUPTURED goster seklindedir, tetikleme Faz 6'da baglanacaktir.
-- MeshBin cekirdegi Faz 3'ten birebir alinmistir (ayni palet/flans/bant).
-- ============================================================================

local AssetService = game:GetService("AssetService")
local Workspace = game:GetService("Workspace")

local assembly = Workspace:WaitForChild("REACTOR_MESH_ASSEMBLY", 60)
if not assembly then
	warn("[FAZ4] REACTOR_MESH_ASSEMBLY bulunamadi; Faz 4.2 kurulumu atlandi.")
	return
end
local staticRoot = assembly:WaitForChild("STATIC", 15)
if not staticRoot then return end

-- Aday: mevcut kit ancak yenisi basariyla olustuktan sonra degistirilir.
-- Eski kitleri su asamada SILME: mesh olusturma hata verebilir.
local previousKits = {}
for _, ch in ipairs(staticRoot:GetChildren()) do
	if ch:GetAttribute("Faz4Generated") and ch:GetAttribute("Faz4DamageKit") then
		previousKits[#previousKits + 1] = ch
	end
end

local ORIGIN_Y = 26.50

local function toStudioPos(x, y, z)
	return Vector3.new(x, ORIGIN_Y + z, -y)
end

local function toStudioVec(vx, vy, vz)
	local v = Vector3.new(vx, vz, -vy)
	local m = v.Magnitude
	return m > 1e-6 and (v / m) or Vector3.new(0, 0, 1)
end


-- ============================================================================
-- MALZEME PALETI (Faz 3 ile birebir + torn_steel/frost)
-- ============================================================================
local MAT_DEFS = {
	nickel_pipe = {rgb = Color3.fromRGB(128, 136, 148), mat = Enum.Material.Metal, refl = 0.09},
	pipe_bore   = {rgb = Color3.fromRGB( 24,  28,  35), mat = Enum.Material.Metal, refl = 0.02},
	gunmetal    = {rgb = Color3.fromRGB( 46,  51,  60), mat = Enum.Material.Metal, refl = 0.04},
	flange      = {rgb = Color3.fromRGB(156, 164, 176), mat = Enum.Material.Metal, refl = 0.11},
	clamp       = {rgb = Color3.fromRGB( 40,  45,  54), mat = Enum.Material.Metal, refl = 0.03},
	cryo_band   = {rgb = Color3.fromRGB( 46, 110, 180), mat = Enum.Material.SmoothPlastic, refl = 0.02},
	torn_steel  = {rgb = Color3.fromRGB( 70,  60,  62), mat = Enum.Material.Metal, refl = 0.05},
	frost       = {rgb = Color3.fromRGB(168, 188, 210), mat = Enum.Material.SmoothPlastic, refl = 0.01},
}

local NON_SHADOW = {}

local function applyMat(part, key)
	local d = MAT_DEFS[key] or MAT_DEFS.gunmetal
	part.Color = d.rgb
	part.Material = d.mat
	part.Reflectance = d.refl or 0
end

local MeshBin = {}
MeshBin.__index = MeshBin

function MeshBin.new()
	return setmetatable({chunks = {}, active = {}}, MeshBin)
end

function MeshBin:getBucket(key, addVertCount)
	addVertCount = addVertCount or 0
	local b = self.active[key]
	if (not b) or (#b.vs + addVertCount > 24000) then
		b = {matKey = key, vs = {}, ns = {}, uvs = {}, fs = {}}
		self.active[key] = b
		self.chunks[#self.chunks + 1] = b
	end
	return b
end

function MeshBin:addRaw(key, v_list, f_list, hardCrease, uvScale)
	local estVerts = hardCrease and (#f_list * 3) or #v_list
	local b = self:getBucket(key, estVerts)
	uvScale = uvScale or 10.0
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


function MeshBin:cylVec(key, aVec, bVec, r, segs, hard, capped)
	local dx, dy, dz = bVec.X - aVec.X, bVec.Y - aVec.Y, bVec.Z - aVec.Z
	local L = math.sqrt(dx * dx + dy * dy + dz * dz)
	if L < 1e-4 then return end
	local fwd = Vector3.new(dx / L, dy / L, dz / L)
	local ref = math.abs(fwd.Z) < 0.92 and Vector3.zAxis or Vector3.xAxis
	local uAx = fwd:Cross(ref).Unit
	local vAx = fwd:Cross(uAx).Unit
	local vs, fs = {}, {}
	for ring = 0, 1 do
		local o = ring == 0 and aVec or bVec
		for j = 0, segs - 1 do
			local th = 2 * math.pi * j / segs
			local p = uAx * (math.cos(th) * r) + vAx * (math.sin(th) * r)
			vs[#vs + 1] = {o.X + p.X, o.Y + p.Y, o.Z + p.Z}
		end
	end
	for j = 0, segs - 1 do
		local k = (j + 1) % segs
		local a, b, c, d = j + 1, k + 1, segs + j + 1, segs + k + 1
		fs[#fs + 1] = {a, b, d}; fs[#fs + 1] = {a, d, c}
	end
	self:addRaw(key, vs, fs, hard == true, 8.0)
	if capped ~= false then
		local cap0, cap1, cf0, cf1 = {{aVec.X, aVec.Y, aVec.Z}}, {{bVec.X, bVec.Y, bVec.Z}}, {}, {}
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
end

function MeshBin:cyl(key, ax, ay, az, bx, by, bz, r, segs, hard)
	self:cylVec(key, Vector3.new(ax, ay, az), Vector3.new(bx, by, bz), r, segs or 12, hard, true)
end

-- GERÇEK İÇİ DELİK (ET KALINLIKLI) ENDÜSTRİYEL BORU PRİMİTİFİ!
-- Dış yüzey (keyOuter, rOut) + İç delik yüzey (keyInner, rIn) + İki uçta halka et kalınlığı!
function MeshBin:hollowPipeVec(keyOuter, aVec, bVec, rOut, rIn, segs, ringStart, ringEnd, keyInner)
	local dx, dy, dz = bVec.X - aVec.X, bVec.Y - aVec.Y, bVec.Z - aVec.Z
	local L = math.sqrt(dx * dx + dy * dy + dz * dz)
	if L < 1e-4 then return end
	segs = segs or 16
	rIn = rIn or (rOut * 0.72)
	keyInner = keyInner or "pipe_bore"
	local fwd = Vector3.new(dx / L, dy / L, dz / L)
	local ref = math.abs(fwd.Z) < 0.92 and Vector3.zAxis or Vector3.xAxis
	local uAx = fwd:Cross(ref).Unit
	local vAx = fwd:Cross(uAx).Unit

	local vOut, fOut = {}, {}
	local vIn,  fIn  = {}, {}
	for ring = 0, 1 do
		local o = ring == 0 and aVec or bVec
		for j = 0, segs - 1 do
			local th = 2 * math.pi * j / segs
			local cs, sn = math.cos(th), math.sin(th)
			local pO = uAx * (cs * rOut) + vAx * (sn * rOut)
			local pI = uAx * (cs * rIn)  + vAx * (sn * rIn)
			vOut[#vOut + 1] = {o.X + pO.X, o.Y + pO.Y, o.Z + pO.Z}
			vIn[#vIn + 1]   = {o.X + pI.X, o.Y + pI.Y, o.Z + pI.Z}
		end
	end
	for j = 0, segs - 1 do
		local k = (j + 1) % segs
		local a, b, c, d = j + 1, k + 1, segs + j + 1, segs + k + 1
		fOut[#fOut + 1] = {a, b, d}; fOut[#fOut + 1] = {a, d, c}
		-- İç cidar normalleri merkeze bakar!
		fIn[#fIn + 1]   = {a, d, b}; fIn[#fIn + 1]   = {a, c, d}
	end
	self:addRaw(keyOuter, vOut, fOut, false, 8.0)
	self:addRaw(keyInner, vIn,  fIn,  false, 8.0)

	if ringStart ~= false then
		local vr, fr = {}, {}
		for j = 1, segs do
			vr[j] = vOut[j]
			vr[segs + j] = vIn[j]
		end
		for j = 0, segs - 1 do
			local k = (j + 1) % segs
			local o0, o1 = j + 1, k + 1
			local i0, i1 = segs + j + 1, segs + k + 1
			fr[#fr + 1] = {o0, i1, o1}; fr[#fr + 1] = {o0, i0, i1}
		end
		self:addRaw(keyOuter, vr, fr, true, 8.0)
	end
	if ringEnd ~= false then
		local vr, fr = {}, {}
		for j = 1, segs do
			vr[j] = vOut[segs + j]
			vr[segs + j] = vIn[segs + j]
		end
		for j = 0, segs - 1 do
			local k = (j + 1) % segs
			local o0, o1 = j + 1, k + 1
			local i0, i1 = segs + j + 1, segs + k + 1
			fr[#fr + 1] = {o0, o1, i1}; fr[#fr + 1] = {o0, i1, i0}
		end
		self:addRaw(keyOuter, vr, fr, true, 8.0)
	end
end

function MeshBin:hollowPipe(keyOuter, ax, ay, az, bx, by, bz, rOut, rIn, segs, ringStart, ringEnd)
	self:hollowPipeVec(keyOuter, Vector3.new(ax, ay, az), Vector3.new(bx, by, bz), rOut, rIn, segs or 16, ringStart, ringEnd)
end

local function alignAxisBasis(axisVec)
	local zt = axisVec.Unit
	local up = math.abs(zt.Z) < 0.92 and Vector3.zAxis or Vector3.xAxis
	local xa = up:Cross(zt).Unit
	local ya = zt:Cross(xa).Unit
	return xa, ya, zt
end

-- GERÇEK ORTASI AÇIK (DELİKLİ) ANSI BORU FLANŞI!
-- Dış etrafı saran yakalı halka (rInner = pipeR * 0.99 -> borunun kendi pipe_bore cidarıyla %0 eş-düzlemli çakışma!)
function MeshBin:hollowFlange(centerVec, axisVec, pipeR, bolts, _rIn)
	bolts = bolts or 8
	local rWrap = pipeR * 0.992
	local xa, ya, zt = alignAxisBasis(axisVec)
	local flR = pipeR * 1.46 + 0.08
	local flT = math.max(0.14, pipeR * 0.28)
	self:hollowPipeVec("flange", centerVec - zt * (flT * 0.46), centerVec + zt * (flT * 0.46), flR, pipeR * 1.18 + 0.04, 18, true, true, "gunmetal")
	self:hollowPipeVec("gunmetal", centerVec - zt * (flT * 0.92), centerVec + zt * (flT * 0.92), pipeR * 1.16 + 0.03, rWrap, 16, true, true, "gunmetal")
	local boltR = pipeR + 0.62 * (flR - pipeR)
	local bRad = math.max(0.035, pipeR * 0.075)
	for bi = 0, bolts - 1 do
		local ang = 2 * math.pi * bi / bolts
		local wp = centerVec + xa * (boltR * math.cos(ang)) + ya * (boltR * math.sin(ang))
		self:cylVec("clamp", wp - zt * (flT * 0.85), wp + zt * (flT * 0.85), bRad, 6, true, true)
	end
end

-- GERÇEK İÇİ DELİK 90° SÜPÜRMELİ BORU DİRSEĞİ!

local emittedCount = 0
function MeshBin:emitToModel(parentModel, namePrefix, collide)
	local jobs = {}
	for idx, b in ipairs(self.chunks) do
		if #b.fs > 0 then
			jobs[#jobs + 1] = {idx = idx, b = b}
		end
	end
	local created = 0
	local BATCH = 10
	local jIdx = 1
	while jIdx <= #jobs do
		local bEnd = math.min(#jobs, jIdx + BATCH - 1)
		local remaining = bEnd - jIdx + 1
		local caller = coroutine.running()
		local resumed = false
		for k = jIdx, bEnd do
			local item = jobs[k]
			task.spawn(function()
				local okRun, errRun = pcall(function()
					local idx, b = item.idx, item.b
					local key = b.matKey
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
						pcall(function() em:Destroy() end)
						error("Mesh content conversion failed: "..tostring(st))
					end
					mp.Name = string.format("%s__%s_%02d", namePrefix, key, idx)
					mp.Anchored = true
					mp.CanCollide = collide == true
					mp.CanTouch = false
					mp.CanQuery = false
					mp.CastShadow = not NON_SHADOW[key]
					mp.CFrame = CFrame.new(center)
					applyMat(mp, key)
					mp.Parent = parentModel
					created += 1
					emittedCount += 1
				end)
				if not okRun then warn("[FAZ4] emit err:", errRun) end
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
		jIdx = bEnd + 1
	end
	return created
end


-- ============================================================================
-- FAZ 4.2 YIRTIK GUDUK URETECLERI (onayli GLB geometrisinin Luau karsiligi)
-- ============================================================================
local function makeRng(seed)
	local s = seed % 2147483647
	if s <= 0 then s += 2147483646 end
	return function()
		s = (s * 16807) % 2147483647
		return (s - 1) / 2147483646
	end
end

local function pipeBasis(fwd) -- hollowPipeVec ile ayni baz (sarmal yonu uyumu)
	local ref = math.abs(fwd.Z) < 0.92 and Vector3.zAxis or Vector3.xAxis
	local uAx = fwd:Cross(ref).Unit
	local vAx = fwd:Cross(uAx).Unit
	return uAx, vAx
end

-- Yirtik guduk: boyuna dikis patlamasi + tek yone sismis, duzensiz disli agiz.
-- Iceri gercek delik (rOut 0.50 / rIn 0.36) + dudakta et kalinligi + don halkasi.
local function tornStub(bin, origin, dir, len, seed, phase, damage)
	local rng = makeRng(seed)
	local uAx, vAx = pipeBasis(dir)
	local NSEG = 36
	local stations = {0, 0.20, 0.42, 0.62, 0.76, 0.87, 0.95, 1.0}
	local rawR, segRand, finger = {}, {}, {}
	for i = 1, NSEG do rawR[i] = 0.45 + 0.55 * rng(); finger[i] = rng() end
	for i = 1, NSEG do
		local prev = rawR[i == 1 and NSEG or i - 1]
		segRand[i] = 0.5 * (rawR[i] + prev)
	end
	local function flare(t)
		if t < 0.76 then return 1 end
		local u = (t - 0.76) / 0.24
		return 1 + 0.34 * damage * (u * u * (3 - 2 * u))
	end
	local function angDist(a, b)
		local d = math.abs(a - b) % (2 * math.pi)
		return math.min(d, 2 * math.pi - d)
	end
	local function deform(th, t, rim, idx)
		local u = t < 0.62 and 0 or (t - 0.62) / 0.38
		local bulge = 0.30 * damage * (math.max(0, math.cos(th - phase)) ^ 2) * u
		local seam = math.exp(-(angDist(th, phase) ^ 2) / (2 * 0.28 ^ 2)) * (0.20 * damage * (u ^ 1.5))
		local k = 1 + bulge + seam
		local ax = 0
		if rim then
			k *= 1 + 0.17 * damage * segRand[idx] * math.sin(7 * th + phase)
			ax = (finger[idx] - 0.55) * 0.16 * len * 0.35 - seam * 0.10
		end
		return k, ax
	end
	local outer, inner = {}, {}
	for si, t in ipairs(stations) do
		local rim = si == #stations
		local ro, ri = {}, {}
		for i = 1, NSEG do
			local th = 2 * math.pi * (i - 1) / NSEG
			local kk, ax = deform(th, t, rim, i)
			local rO = 0.50 * flare(t) * kk
			local pO = origin + uAx * (rO * math.cos(th)) + vAx * (rO * math.sin(th)) + dir * (t * len + ax)
			ro[i] = {pO.X, pO.Y, pO.Z}
			local rI = 0.36 * flare(t) * (1 + (kk - 1) * 0.85)
			local aI = t * len + ax
			if rim then aI -= 0.09 end
			local pI = origin + uAx * (rI * math.cos(th)) + vAx * (rI * math.sin(th)) + dir * aI
			ri[i] = {pI.X, pI.Y, pI.Z}
		end
		outer[si] = ro; inner[si] = ri
	end
	local function stripAdd(key, rings, i0, i1, flip, hard)
		local vs, fs = {}, {}
		for si = i0, i1 do
			for i = 1, NSEG do vs[#vs + 1] = rings[si][i] end
		end
		for b = 0, (i1 - i0 - 1) do
			local ob = b * NSEG
			for j = 0, NSEG - 1 do
				local k = (j + 1) % NSEG
				local a, bb, c, d = ob + j + 1, ob + k + 1, ob + NSEG + j + 1, ob + NSEG + k + 1
				if flip then
					fs[#fs + 1] = {a, d, bb}; fs[#fs + 1] = {a, c, d}
				else
					fs[#fs + 1] = {a, bb, d}; fs[#fs + 1] = {a, d, c}
				end
			end
		end
		bin:addRaw(key, vs, fs, hard == true, 8.0)
	end
	stripAdd("nickel_pipe", outer, 1, 6, false, false)
	stripAdd("torn_steel", outer, 6, 8, false, true)
	stripAdd("pipe_bore", inner, 1, 8, true, false)
	local function annulus(key, ro, ri, isEnd)
		local vs, fs = {}, {}
		for i = 1, NSEG do vs[i] = ro[i]; vs[NSEG + i] = ri[i] end
		for j = 0, NSEG - 1 do
			local k = (j + 1) % NSEG
			local o0, o1, i0, i1 = j + 1, k + 1, NSEG + j + 1, NSEG + k + 1
			if isEnd then
				fs[#fs + 1] = {o0, o1, i1}; fs[#fs + 1] = {o0, i1, i0}
			else
				fs[#fs + 1] = {o0, i1, o1}; fs[#fs + 1] = {o0, i0, i1}
			end
		end
		bin:addRaw(key, vs, fs, true, 8.0)
	end
	annulus("torn_steel", outer[8], inner[8], true)
	annulus("nickel_pipe", outer[1], inner[1], false)
	-- don halkasi: ic cidar, agza yakin iki istasyon
	local fr = {}
	for si = 6, 7 do
		local t = stations[si]
		local ring = {}
		for i = 1, NSEG do
			local th = 2 * math.pi * (i - 1) / NSEG
			local r = (0.36 - 0.014) * flare(t)
			local p = origin + uAx * (r * math.cos(th)) + vAx * (r * math.sin(th)) + dir * (t * len)
			ring[i] = {p.X, p.Y, p.Z}
		end
		fr[si] = ring
	end
	stripAdd("frost", fr, 6, 7, true, false)
	return origin + dir * len, uAx, vAx
end

-- Kivrik yirtik metal seridi (cift yuz)
local function curledShard(bin, base, uAx, vAx, fwd, th, rBase, ln)
	local cw, sw = math.cos(th), math.sin(th)
	local curl, w = 0.9, 0.16
	local vs, fs = {}, {}
	local steps = 4
	for s = 0, steps do
		local u = s / steps
		local rr = rBase + 0.30 * u + curl * 0.16 * u * u
		local ax = ln * u - curl * 0.22 * u * u
		local c = base + uAx * (rr * cw) + vAx * (rr * sw) + fwd * ax
		local tw = (uAx * (-sw) + vAx * cw) * (w * 0.5 * (1 - 0.5 * u))
		local p1, p2 = c - tw, c + tw
		vs[#vs + 1] = {p1.X, p1.Y, p1.Z}
		vs[#vs + 1] = {p2.X, p2.Y, p2.Z}
	end
	for s = 0, steps - 1 do
		local a = 2 * s + 1
		fs[#fs + 1] = {a, a + 2, a + 3}; fs[#fs + 1] = {a, a + 3, a + 1}
		fs[#fs + 1] = {a, a + 3, a + 2}; fs[#fs + 1] = {a, a + 1, a + 3}
	end
	bin:addRaw("torn_steel", vs, fs, true, 8.0)
end

-- Yarilmis / firlamis kriyo bant parcasi (kismi yay, cift yuz)
local function splitBandStrip(bin, center, dir, r, arc0, arc1, tilt)
	local uAx, vAx = pipeBasis(dir)
	local width = 0.48
	local n = 22
	local vs, fs = {}, {}
	for k = 0, n do
		local th = arc0 + (arc1 - arc0) * k / n
		for _, sgn in ipairs({-0.5, 0.5}) do
			local p = center + uAx * (r * math.cos(th)) + vAx * (r * math.sin(th))
				+ dir * (sgn * width + tilt * math.cos(th) * width)
			vs[#vs + 1] = {p.X, p.Y, p.Z}
		end
	end
	for k = 0, n - 1 do
		local a = 2 * k + 1
		fs[#fs + 1] = {a, a + 2, a + 3}; fs[#fs + 1] = {a, a + 3, a + 1}
		fs[#fs + 1] = {a, a + 3, a + 2}; fs[#fs + 1] = {a, a + 1, a + 3}
	end
	bin:addRaw("cryo_band", vs, fs, true, 8.0)
end

-- Agiz ankraji: hacimsel sizinti hunisi icin gorunmez dayanak (Faz 6 kullanacak)
local function makeAnchor(parent, name, authorPos, authorDir)
	local a = Instance.new("Part")
	a.Name = name
	a.Size = Vector3.new(0.2, 0.2, 0.2)
	a.Transparency = 1
	a.CanCollide = false
	a.CanQuery = false
	a.CanTouch = false
	a.Anchored = true
	a.CastShadow = false
	a:SetAttribute("Faz4MouthAnchor", true)
	local p = toStudioPos(authorPos.X, authorPos.Y, authorPos.Z)
	local dv = toStudioVec(authorDir.X, authorDir.Y, authorDir.Z)
	a.CFrame = CFrame.lookAt(p, p + dv)
	a.Parent = parent
end

local function buildRupturedSpool(kit, spoolId, p0, p1, bands, seedBase)
	local model = Instance.new("Model")
	model.Name = "PIPE_SPOOL_" .. spoolId .. "_RUPTURED"
	model:SetAttribute("Faz4RupturedSpool", true)
	model:SetAttribute("SpoolId", spoolId)
	model.Parent = kit

	local bin = MeshBin.new()
	local dir = (p1 - p0).Unit
	local L = (p1 - p0).Magnitude
	bin:hollowFlange(p0 + dir * 0.16, dir, 0.50, 10)
	bin:hollowFlange(p1 - dir * 0.16, dir, 0.50, 10)

	local lenA, lenB = 0.42 * L, 0.40 * L
	local phaseA = (seedBase % 628) / 100
	local mouthA, uA, vA = tornStub(bin, p0, dir, lenA, seedBase, phaseA, 0.9)
	local perp = (pipeBasis(dir))
	local dB = (-dir + perp * math.tan(math.rad(3.0))).Unit
	local orgB = p1 + perp * 0.09
	local mouthB, uB, vB = tornStub(bin, orgB, dB, lenB, seedBase + 37, phaseA + 2.0, 1.25)

	local shardThA = {0.6, 2.5, 4.4}
	local shardLnA = {0.34, 0.30, 0.26}
	for i, th in ipairs(shardThA) do
		curledShard(bin, mouthA - dir * 0.10, uA, vA, dir, th + phaseA, 0.58, shardLnA[i])
	end
	for _, th in ipairs({1.4, 3.9}) do
		curledShard(bin, mouthB - dB * 0.10, uB, vB, dB, th + phaseA, 0.60, 0.42)
	end

	for _, sb in ipairs(bands) do
		local c = p0 + dir * sb
		if sb < lenA - 0.35 then
			bin:hollowPipeVec("cryo_band", c - dir * 0.24, c + dir * 0.24, 0.535, 0.495, 16, true, true)
		elseif sb > L - lenB + 0.15 then
			splitBandStrip(bin, c + perp * 0.09, dB, 0.545, 0.4, 4.1, 0.16)
			splitBandStrip(bin, c + perp * 0.09 - dir * 0.05, dB, 0.545, 4.5, 6.0, 0.16)
		else
			splitBandStrip(bin, p0 + dir * (lenA - 0.55), dir, 0.545, 1.1, 4.6, 0.22)
		end
	end

	local boltP = mouthA - dir * 0.04 + uA * 0.60
	bin:cylVec("clamp", boltP - dir * 0.10, boltP + dir * 0.16 + vA * 0.06, 0.0375, 6, true, true)

	bin:emitToModel(model, "PIPE_SPOOL_" .. spoolId .. "_RUPTURED")

	-- Gizli dogar: hasar anina kadar gorunmez
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("MeshPart") then
			d.Transparency = 1
			d.CastShadow = false
		end
	end
	makeAnchor(model, "MOUTH_A", mouthA, dir)
	makeAnchor(model, "MOUTH_B", mouthB, dB)
end

-- ============================================================================
-- KIT KURULUMU (author koordinatlari Faz 3 spool tarifleriyle birebir)
-- ============================================================================
local kit = Instance.new("Model")
kit.Name = "DAMAGE_PIPE_RUPTURE_KIT_01"
kit:SetAttribute("Faz4Generated", true)
kit:SetAttribute("Faz4DamageKit", true)
-- Parent verilmez: eksik geometri sahneye cikmaz.
local ok, err = pcall(function()
	local V = Vector3.new
	buildRupturedSpool(kit, "UPPER_LEFT",  V(-19.95, -8.20, 15.85), V(-19.95, -1.20, 15.85), {2.0, 5.0}, 1101)
	buildRupturedSpool(kit, "UPPER_RIGHT", V( 19.95, -8.20, 15.85), V( 19.95, -1.20, 15.85), {2.0, 5.0}, 2202)
	buildRupturedSpool(kit, "REAR_LEFT",   V(-19.95, 10.80,  7.80), V(-19.95, 10.80,  1.60), {3.1}, 3303)
	buildRupturedSpool(kit, "REAR_RIGHT",  V( 19.95, 10.80,  7.80), V( 19.95, 10.80,  1.60), {3.1}, 4404)
	local count, anchors, spools = 0, 0, 0
	for _, d in ipairs(kit:GetDescendants()) do
		if d:IsA("MeshPart") then
			assert(d.MeshContent.SourceType ~= Enum.ContentSourceType.None or d.MeshId ~= "", "Bos mesh: "..d.Name)
			count += 1
		end
		if d:GetAttribute("Faz4MouthAnchor") then anchors += 1 end
		if d:GetAttribute("Faz4RupturedSpool") then spools += 1 end
	end
	assert(count == 32 and anchors == 8 and spools == 4,
		string.format("Eksik kit: %d mesh, %d anchor, %d spool", count, anchors, spools))
	kit.Parent = staticRoot
end)
if not ok then
	kit:Destroy()
	warn("[FAZ4] Yeni hasar kiti tamamlanamadi; eski kit korundu: " .. tostring(err))
	return
end
for _, oldKit in ipairs(previousKits) do oldKit:Destroy() end
print(string.format("[FAZ4] DAMAGE_PIPE_RUPTURE_KIT_01 kuruldu (%d MeshPart, gizli; 8 agiz ankraji)", emittedCount))
