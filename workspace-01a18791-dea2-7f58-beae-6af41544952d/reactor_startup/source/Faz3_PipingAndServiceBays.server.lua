--!nonstrict
-- ============================================================================
-- FAZ 3 (PAKET B — REV2: 360° BAĞLANTILI & GERÇEK İÇİ DELİK BORU MİMARİSİ)
-- REAKTÖR KRİYOJENİK BORULAMA AĞI (M11) & 6 PİSTON ARKASI SERVİS GALERİSİ (M12)
-- ============================================================================
--   * %100 Gerçek 3B MeshPart mimarisi (%0 ParticleEmitter / Beam / BillboardGui;
--     CreateDataModelContentAsync + em:Destroy() ile %0 canlı EditableMesh sızıntısı).
--   * GERÇEK İÇİ DELİK BORULAR (hollowPipe + hollowFlange + hollowElbow90):
--     Düz dolu silindir yerine dış kabuk (rOut) + iç delik cidar (rIn) + et kalınlığı
--     halkaları ile modellenmiş gerçek endüstriyel çelik borular!
--   * %0 KESİK / HAVADA BİTEN UÇ (İçeriden, dışarıdan ve arkadan 360° tam kapalı devre):
--     - Üst arka branşmanlar arka duvar arkasından dirseklerle inip Kondenser Plenum
--       tavan kollektörlerine flanşla bağlanır.
--     - Üst ve alt YG kablo tavaları her iki uçta zırhlı şalt dolaplarına girer.
--     - 6 servis galerisinin tamamında tavan boruları, akümülatör ön/arka uçları ve
--       teleskopik piston arka gövdesi (-33.80) çelik kaidelere ve kollektörlere bağlıdır.
--     - Tüm 6 galeride (SL-00..SL-05) zemin ızgarası altta ve MAINT-BAY yazıları %100 DÜZ!
-- ============================================================================

local AssetService = game:GetService("AssetService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local assembly = Workspace:WaitForChild("REACTOR_MESH_ASSEMBLY", 60)
local world = RunService:IsRunning()
	and Workspace:WaitForChild("CORE_PROTOCOL_V2_WORLD", 25)
	or Workspace:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
if not assembly then
	warn("[FAZ3] REACTOR_MESH_ASSEMBLY bulunamadı; Faz 3 kurulumu atlandı.")
	return
end
local staticRoot = assembly:WaitForChild("STATIC", 15)
local movingRoot = assembly:WaitForChild("MOVING", 15)
if not staticRoot or not movingRoot then return end

-- Temiz idempotensi: yeniden çalıştırılırsa önceki Faz 3 örneklerini sil
for _, container in ipairs({staticRoot, movingRoot}) do
	for _, ch in ipairs(container:GetChildren()) do
		if ch:GetAttribute("Faz3Generated") then
			ch:Destroy()
		end
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
-- 1. ÇOK TONLU ARDUVAZ / GRAFİT / NİKEL-ÇELİK MALZEME PALETİ
-- ============================================================================
local MAT_DEFS = {
	nickel_pipe = {rgb = Color3.fromRGB(128, 136, 148), mat = Enum.Material.Metal, refl = 0.09},
	slate_pipe  = {rgb = Color3.fromRGB( 84,  92, 106), mat = Enum.Material.Metal, refl = 0.06},
	pipe_bore   = {rgb = Color3.fromRGB( 24,  28,  35), mat = Enum.Material.Metal, refl = 0.02},
	gunmetal    = {rgb = Color3.fromRGB( 46,  51,  60), mat = Enum.Material.Metal, refl = 0.04},
	flange      = {rgb = Color3.fromRGB(156, 164, 176), mat = Enum.Material.Metal, refl = 0.11},
	clamp       = {rgb = Color3.fromRGB( 40,  45,  54), mat = Enum.Material.Metal, refl = 0.03},
	cryo_band   = {rgb = Color3.fromRGB( 46, 110, 180), mat = Enum.Material.SmoothPlastic, refl = 0.02},
	hv_tray     = {rgb = Color3.fromRGB( 64,  70,  82), mat = Enum.Material.Metal, refl = 0.05},
	conduit_blu = {rgb = Color3.fromRGB( 40,  86, 148), mat = Enum.Material.SmoothPlastic, refl = 0.01},
	conduit_slv = {rgb = Color3.fromRGB(138, 146, 158), mat = Enum.Material.Metal, refl = 0.08},
	caution     = {rgb = Color3.fromRGB(192, 170,  58), mat = Enum.Material.SmoothPlastic, refl = 0},
	valve_rim   = {rgb = Color3.fromRGB(132,  52,  50), mat = Enum.Material.Metal, refl = 0.02},
	gauge_face  = {rgb = Color3.fromRGB(214, 228, 242), mat = Enum.Material.Neon, refl = 0},
	vault_upper = {rgb = Color3.fromRGB( 98, 110, 130), mat = Enum.Material.Metal, refl = 0.04},
	vault_mid   = {rgb = Color3.fromRGB( 70,  75,  88), mat = Enum.Material.Metal, refl = 0.03},
	vault_lower = {rgb = Color3.fromRGB( 70,  68,  60), mat = Enum.Material.Metal, refl = 0.02},
	grate_rib   = {rgb = Color3.fromRGB( 88,  95, 108), mat = Enum.Material.Metal, refl = 0.06},
	dark        = {rgb = Color3.fromRGB( 18,  22,  29), mat = Enum.Material.SmoothPlastic, refl = 0},
	bay_lamp    = {rgb = Color3.fromRGB(216, 232, 248), mat = Enum.Material.Neon, refl = 0},
	status_cyan = {rgb = Color3.fromRGB( 74, 178, 244), mat = Enum.Material.Neon, refl = 0},
}

local NON_SHADOW = {
	gauge_face = true, bay_lamp = true, status_cyan = true,
}

local function applyMat(part, key)
	local d = MAT_DEFS[key] or MAT_DEFS.gunmetal
	part.Color = d.rgb
	part.Material = d.mat
	part.Reflectance = d.refl or 0
end

-- ============================================================================
-- 2. SIFIR SIZINTILI 3B MESH TOPLAYICI + GERÇEK İÇİ DELİK BORU PRİMİTİFLERİ
-- ============================================================================
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

function MeshBin:box(key, cx, cy, cz, sx, sy, sz, rotCF)
	local hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
	local corners = {
		{-hx, -hy, -hz}, { hx, -hy, -hz}, { hx,  hy, -hz}, {-hx,  hy, -hz},
		{-hx, -hy,  hz}, { hx, -hy,  hz}, { hx,  hy,  hz}, {-hx,  hy,  hz},
	}
	local vs = {}
	for i, c in ipairs(corners) do
		if rotCF then
			local p = rotCF:PointToWorldSpace(Vector3.new(c[1], c[2], c[3]))
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
	self:addRaw(key, vs, fs, true, 10.0)
end

-- Yalnızca cıvata pimleri, korkuluk çubukları ve manometre gövdesi için dolu çubuk/disk
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
function MeshBin:hollowElbow90(matKey, cornerVec, dirIn, dirOut, bendR, pipeR, segs, flanged)
	segs = segs or 7
	local rIn = pipeR * 0.72
	local uIn = dirIn.Unit
	local uOut = dirOut.Unit
	local pStart = cornerVec - uIn * bendR
	local pEnd = cornerVec + uOut * bendR
	local cArc = cornerVec - uIn * bendR + uOut * bendR
	local e1 = pStart - cArc
	local e2 = pEnd - cArc
	local pts = {}
	for i = 0, segs do
		local th = 0.5 * math.pi * (i / segs)
		pts[i + 1] = cArc + e1 * math.cos(th) + e2 * math.sin(th)
	end
	for i = 1, segs do
		local a = pts[i]
		local b = pts[i + 1]
		local dir = (b - a).Unit
		self:hollowPipeVec(matKey, a - dir * (pipeR * 0.09), b + dir * (pipeR * 0.09), pipeR * 1.005, rIn, 14, i == 1, i == segs, "pipe_bore")
	end
	if flanged ~= false then
		self:hollowFlange(pStart, uIn, pipeR, 8, rIn)
		self:hollowFlange(pEnd, uOut, pipeR, 8, rIn)
	end
	return pStart, pEnd
end

function MeshBin:handwheelValve(posVec, pipeAxis, wheelDir, pipeR)
	local pa = pipeAxis.Unit
	local wd = wheelDir.Unit
	local rIn = pipeR * 0.72
	self:hollowPipeVec("gunmetal", posVec - pa * 0.85, posVec + pa * 0.85, pipeR * 1.32, rIn, 16, true, true, "pipe_bore")
	self:hollowFlange(posVec - pa * 0.85, pa, pipeR, 8, rIn)
	self:hollowFlange(posVec + pa * 0.85, pa, pipeR, 8, rIn)
	local bonnetTop = posVec + wd * (pipeR * 2.55)
	self:cylVec("gunmetal", posVec + wd * (pipeR * 0.90), posVec + wd * (pipeR * 1.65), pipeR * 0.72, 12, false, true)
	self:hollowFlange(posVec + wd * (pipeR * 1.45), wd, pipeR * 0.62, 6, pipeR * 0.22)
	self:cylVec("flange", posVec + wd * (pipeR * 1.45), bonnetTop, pipeR * 0.24, 10, false, true)
	local xa, ya, _ = alignAxisBasis(wd)
	local wheelR = math.max(0.88, pipeR * 1.85)
	local nRim = 14
	for i = 0, nRim - 1 do
		local a0 = 2 * math.pi * i / nRim
		local a1 = 2 * math.pi * (i + 1) / nRim
		local q0 = bonnetTop + xa * (wheelR * math.cos(a0)) + ya * (wheelR * math.sin(a0))
		local q1 = bonnetTop + xa * (wheelR * math.cos(a1)) + ya * (wheelR * math.sin(a1))
		self:cylVec("valve_rim", q0, q1, 0.085, 8, false, true)
	end
	for i = 0, 4 do
		local ang = 2 * math.pi * i / 5
		local q = bonnetTop + xa * (wheelR * math.cos(ang)) + ya * (wheelR * math.sin(ang))
		self:cylVec("flange", bonnetTop, q, 0.06, 6, false, true)
	end
end

function MeshBin:pressureGauge(posVec, faceNormal)
	local fn = faceNormal.Unit
	self:cylVec("gunmetal", posVec - fn * 0.14, posVec + fn * 0.14, 0.44, 16, false, true)
	self:cylVec("flange", posVec + fn * 0.08, posVec + fn * 0.18, 0.47, 16, false, true)
	self:cylVec("gauge_face", posVec + fn * 0.14, posVec + fn * 0.21, 0.37, 16, false, true)
end

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
						mp = AssetService:CreateMeshPartAsync(Content.fromObject(em))
						pcall(function() em:Destroy() end)
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
				if not okRun then warn("[FAZ3] emit err:", errRun) end
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

local function makeSubModel(parent, name)
	local m = Instance.new("Model")
	m.Name = name
	m:SetAttribute("Faz3Generated", true)
	m.Parent = parent
	return m
end

-- ============================================================================
-- 3. MODEL M11 — REACTOR_COOLANT_PIPING_RING_01 (GERÇEK İÇİ DELİK BORULAR,
--    %0 KESİK UÇ, ARKA KONDENSER BAĞLANTISI & 4 FLANŞLI KOPMA MODÜLÜ)
-- ============================================================================
local mPiping = makeSubModel(staticRoot, "REACTOR_COOLANT_PIPING_RING_01")
do
	local binMain = MeshBin.new()

	for _, side in ipairs({-1, 1}) do
		local stag = side < 0 and "LEFT" or "RIGHT"
		local xMain, zMain, rMain = side * 19.95, 15.85, 0.50
		local xRet,  zRet,  rRet  = side * 21.35, 14.15, 0.33

		local nWall = Vector3.new(side * 0.768, 0, 0.640).Unit
		local yWall = Vector3.new(0, 1, 0)
		local tWall = nWall:Cross(yWall).Unit
		local rotBr = CFrame.fromMatrix(Vector3.zero, nWall, yWall, tWall)

		-- A) Ön zırhlı duvar kollektör sandığı (dışarıya veya havaya taşan kesik boru YOK!)
		local chestPos = Vector3.new(side * 21.75, -16.85, 15.15)
		binMain:box("gunmetal", chestPos.X, chestPos.Y, chestPos.Z, 1.35, 2.35, 3.85, rotBr)
		binMain:box("flange", chestPos.X - nWall.X * 0.64, chestPos.Y, chestPos.Z - nWall.Z * 0.64, 0.14, 2.15, 3.60, rotBr)

		local cFrontMain = Vector3.new(xMain, -16.85, zMain)
		binMain:hollowPipeVec("nickel_pipe", Vector3.new(side * 21.55, -16.85, zMain), cFrontMain + Vector3.new(side * 1.25, 0, 0), rMain, rMain * 0.72, 16, true, true)
		local _, yStartM = binMain:hollowElbow90("nickel_pipe", cFrontMain, Vector3.new(-side, 0, 0), Vector3.new(0, 1, 0), 1.25, rMain, 7, true)

		-- Üst 45° eğim flanşlı kopma modülü (PIPE_SPOOL_UPPER_LEFT / RIGHT — Y = -8.20 .. -1.20)
		local ySp0, ySp1 = -8.20, -1.20
		binMain:hollowPipeVec("nickel_pipe", yStartM, Vector3.new(xMain, ySp0, zMain), rMain, rMain * 0.72, 16, true, true)
		binMain:hollowFlange(Vector3.new(xMain, ySp0, zMain), Vector3.new(0, 1, 0), rMain, 10)

		local mSpoolUpper = makeSubModel(mPiping, "PIPE_SPOOL_UPPER_" .. stag)
		mSpoolUpper:SetAttribute("Faz3RuptureSpool", true)
		mSpoolUpper:SetAttribute("SpoolId", "UPPER_" .. stag)
		local binSpoolU = MeshBin.new()
		binSpoolU:hollowPipe("nickel_pipe", xMain, ySp0, zMain, xMain, ySp1, zMain, rMain, rMain * 0.72, 16, true, true)
		binSpoolU:hollowFlange(Vector3.new(xMain, ySp0 + 0.16, zMain), Vector3.new(0, 1, 0), rMain, 10)
		binSpoolU:hollowFlange(Vector3.new(xMain, ySp1 - 0.16, zMain), Vector3.new(0, 1, 0), rMain, 10)
		for _, yb in ipairs({-6.2, -3.2}) do
			binSpoolU:hollowPipe("cryo_band", xMain, yb - 0.24, zMain, xMain, yb + 0.24, zMain, rMain * 1.07, rMain * 0.99, 16, true, true)
		end
		binSpoolU:emitToModel(mSpoolUpper, "PIPE_SPOOL_UPPER_" .. stag)

		binMain:hollowFlange(Vector3.new(xMain, ySp1, zMain), Vector3.new(0, 1, 0), rMain, 10)
		binMain:hollowPipe("nickel_pipe", xMain, ySp1, zMain, xMain, 9.55, zMain, rMain, rMain * 0.72, 16, true, true)
		for _, yb in ipairs({-12.2, 2.8, 6.8}) do
			binMain:hollowPipe("cryo_band", xMain, yb - 0.24, zMain, xMain, yb + 0.24, zMain, rMain * 1.07, rMain * 0.99, 16, true, true)
		end
		binMain:hollowFlange(Vector3.new(xMain, 4.80, zMain), Vector3.new(0, 1, 0), rMain, 10)

		-- İkincil dönüş hattı (üst 45° eğim — ön kollektör sandığına tam bağlı!)
		local cFrontRet = Vector3.new(xRet, -16.65, zRet)
		binMain:hollowPipeVec("slate_pipe", Vector3.new(side * 22.35, -16.65, zRet), cFrontRet + Vector3.new(side * 0.95, 0, 0), rRet, rRet * 0.72, 14, true, true)
		local _, yStartR = binMain:hollowElbow90("slate_pipe", cFrontRet, Vector3.new(-side, 0, 0), Vector3.new(0, 1, 0), 0.95, rRet, 6, true)
		binMain:hollowPipeVec("slate_pipe", yStartR, Vector3.new(xRet, 8.85, zRet), rRet, rRet * 0.72, 14, true, true)
		for _, yf in ipairs({-10.5, -3.5, 3.5}) do
			binMain:hollowFlange(Vector3.new(xRet, yf, zRet), Vector3.new(0, 1, 0), rRet, 8)
		end

		-- Üst 45° C-profil duvar kelepçeleri
		for _, ycB in ipairs({-13.4, -9.4, -4.7, 0.4, 5.6, 8.4}) do
			local midP = (Vector3.new(xMain, ycB, zMain) + Vector3.new(xRet, ycB, zRet)) * 0.5 + nWall * 0.58
			binMain:box("clamp", midP.X, midP.Y, midP.Z, 0.95, 0.44, 3.45, rotBr)
			binMain:hollowPipe("flange", xMain, ycB - 0.18, zMain, xMain, ycB + 0.18, zMain, rMain * 1.18, rMain * 0.98, 14, true, true)
			binMain:hollowPipe("flange", xRet,  ycB - 0.18, zRet,  xRet,  ycB + 0.18, zRet,  rRet * 1.18,  rRet * 0.98,  12, true, true)
		end

		-- B) Arka köşe dikey kollektör inişi + PIPE_SPOOL_REAR_* + Kollu Vana + Manometre + Radyatör bağlantısı
		local cTopDrop = Vector3.new(xMain, 10.80, zMain)
		local _, pDropTop = binMain:hollowElbow90("nickel_pipe", cTopDrop, Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), 1.25, rMain, 7, true)

		local zRspHi, zRspLo = 7.80, 1.60
		binMain:hollowPipeVec("nickel_pipe", pDropTop, Vector3.new(xMain, 10.80, zRspHi), rMain, rMain * 0.72, 16, true, true)
		binMain:hollowFlange(Vector3.new(xMain, 10.80, zRspHi), Vector3.new(0, 0, -1), rMain, 10)

		local mSpoolRear = makeSubModel(mPiping, "PIPE_SPOOL_REAR_" .. stag)
		mSpoolRear:SetAttribute("Faz3RuptureSpool", true)
		mSpoolRear:SetAttribute("SpoolId", "REAR_" .. stag)
		local binSpoolR = MeshBin.new()
		binSpoolR:hollowPipe("nickel_pipe", xMain, 10.80, zRspHi, xMain, 10.80, zRspLo, rMain, rMain * 0.72, 16, true, true)
		binSpoolR:hollowFlange(Vector3.new(xMain, 10.80, zRspHi - 0.16), Vector3.new(0, 0, -1), rMain, 10)
		binSpoolR:hollowFlange(Vector3.new(xMain, 10.80, zRspLo + 0.16), Vector3.new(0, 0, -1), rMain, 10)
		binSpoolR:hollowPipe("cryo_band", xMain, 10.80, 4.70 - 0.24, xMain, 10.80, 4.70 + 0.24, rMain * 1.07, rMain * 0.99, 16, true, true)
		binSpoolR:emitToModel(mSpoolRear, "PIPE_SPOOL_REAR_" .. stag)

		binMain:hollowFlange(Vector3.new(xMain, 10.80, zRspLo), Vector3.new(0, 0, -1), rMain, 10)
		binMain:hollowPipe("nickel_pipe", xMain, 10.80, zRspLo, xMain, 10.80, -12.35, rMain, rMain * 0.72, 16, true, true)

		-- Kollu Kesme Vanası + Çift Işıklı Analog Manometre Bloğu
		binMain:handwheelValve(Vector3.new(xMain, 10.80, -2.60), Vector3.new(0, 0, -1), Vector3.new(-side * 0.55, -0.835, 0), rMain)
		binMain:box("gunmetal", xMain - side * 0.55, 10.55, -5.80, 0.95, 0.85, 1.45)
		binMain:pressureGauge(Vector3.new(xMain - side * 0.58, 10.05, -5.45), Vector3.new(0, -1, 0))
		binMain:pressureGauge(Vector3.new(xMain - side * 0.58, 10.05, -6.25), Vector3.new(0, -1, 0))
		binMain:box("status_cyan", xMain - side * 0.96, 10.22, -5.80, 0.08, 0.14, 0.92)

		-- İkincil dönüş dikey inişi
		local cRetDrop = Vector3.new(xRet, 9.80, zRet)
		local _, pRDrop = binMain:hollowElbow90("slate_pipe", cRetDrop, Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), 0.95, rRet, 6, true)
		binMain:hollowPipeVec("slate_pipe", pRDrop, Vector3.new(xRet, 9.80, -11.60), rRet, rRet * 0.72, 14, true, true)
		for _, zrC in ipairs({9.2, 3.2, -4.4, -9.8}) do
			binMain:box("clamp", side * 20.95, 10.55, zrC, 2.45, 1.55, 0.38)
		end

		-- Alt zeytuni-gri radyatör yan kollektör sandığı + tam flanşlı bağlantı!
		binMain:box("gunmetal", side * 18.05, 13.55, -13.10, 0.85, 1.35, 2.85)
		local cBotTurn = Vector3.new(xMain, 10.80, -13.60)
		local _, pToRad = binMain:hollowElbow90("nickel_pipe", cBotTurn, Vector3.new(0, 0, -1), Vector3.new(0, 1, 0), 1.25, rMain, 7, true)
		binMain:hollowPipeVec("nickel_pipe", pToRad, Vector3.new(xMain, 12.60, -13.60), rMain, rMain * 0.72, 16, true, true)
		local cRadIn = Vector3.new(xMain, 13.55, -13.60)
		local _, pRadPlug = binMain:hollowElbow90("nickel_pipe", cRadIn, Vector3.new(0, 1, 0), Vector3.new(-side, 0, 0), 0.95, rMain, 6, true)
		binMain:hollowPipeVec("nickel_pipe", pRadPlug, Vector3.new(side * 17.85, 13.55, -13.60), rMain, rMain * 0.72, 16, true, true)
		binMain:hollowFlange(Vector3.new(side * 18.28, 13.55, -13.60), Vector3.new(-side, 0, 0), rMain, 10)

		local cRBot = Vector3.new(xRet, 9.80, -12.55)
		local _, pR1 = binMain:hollowElbow90("slate_pipe", cRBot, Vector3.new(0, 0, -1), Vector3.new(-side * 0.58, 0.815, 0), 0.95, rRet, 6, true)
		binMain:hollowPipeVec("slate_pipe", pR1, Vector3.new(side * 17.85, 13.55, -12.55), rRet, rRet * 0.72, 14, true, true)
		binMain:hollowFlange(Vector3.new(side * 18.28, 13.55, -12.55), Vector3.new(-side, 0, 0), rRet, 8)

		-- C) Üst arka plenum köprü bağlantısı (ana iniş kollektöründen yatay köprü borusuna T-bağlantı!)
		local cBridge = Vector3.new(xMain, 10.80, 15.85)
		binMain:hollowPipe("slate_pipe", xMain, 10.80, 15.85, side * 16.55, 13.85, 18.55, 0.34, 0.24, 14, true, true)
		binMain:hollowFlange(Vector3.new(cBridge.X - side * 0.35, 11.15, 16.15), Vector3.new(-side, 0.8, 0.6), 0.34, 8)
		binMain:hollowFlange(Vector3.new(side * 16.55, 13.85, 18.55), Vector3.new(-side, 0, 0), 0.38, 8)

		-- D) Üst 45° Yüksek Gerilim Kablo Tavası — her iki uçta zırhlı şalt dolabına girer (%0 kesik uç!)
		local xTr, zTr = side * 17.55, 18.45
		local trCenter = Vector3.new(xTr, -2.10, zTr)
		binMain:box("hv_tray", trCenter.X, trCenter.Y, trCenter.Z, 0.14, 30.20, 1.35, rotBr)
		for _, rS in ipairs({-0.62, 0.62}) do
			local offR = tWall * rS - nWall * 0.12
			binMain:box("clamp", trCenter.X + offR.X, trCenter.Y + offR.Y, trCenter.Z + offR.Z, 0.28, 30.20, 0.10, rotBr)
		end
		-- Ön ve Arka YG Şalt/Bağlantı Dolapları (kademeli kapak -> %0 Z-fight!)
		for _, yBox in ipairs({-17.25, 13.05}) do
			local bp = Vector3.new(xTr, yBox, zTr) - nWall * 0.10
			binMain:box("gunmetal", bp.X, bp.Y, bp.Z, 0.84, 1.25, 1.78, rotBr)
			binMain:box("flange", bp.X - nWall.X * 0.50, bp.Y, bp.Z - nWall.Z * 0.50, 0.08, 1.05, 1.54, rotBr)
		end
		for _, cb in ipairs({{-0.34, "conduit_blu"}, {0.0, "conduit_slv"}, {0.34, "cryo_band"}}) do
			local cp0 = Vector3.new(xTr, -17.30, zTr) + tWall * cb[1] - nWall * 0.24
			local cp1 = Vector3.new(xTr,  13.10, zTr) + tWall * cb[1] - nWall * 0.24
			binMain:hollowPipeVec(cb[2], cp0, cp1, 0.105, 0.072, 10, false, false)
		end
		-- Arka YG şalt dolabından aşağı radyatör besleme kutusuna zırhlı dikey kablo inişi!
		binMain:hollowPipe("conduit_slv", side * 17.85, 13.25, 17.85, side * 17.85, 13.25, -11.95, 0.16, 0.11, 10, true, true)
		for _, yt in ipairs({-13.0, -7.5, -2.0, 3.5, 9.0}) do
			local tp = Vector3.new(xTr, yt, zTr) - nWall * 0.26
			binMain:box("caution", tp.X, tp.Y, tp.Z, 0.08, 0.28, 1.24, rotBr)
		end

		-- E) Alt Çukur Taban Dönüş Kollektörü & YG Bara Kanalı (Z_src >= -21.42 -> taban plakasıyla %0 çakışma!)
		local xFl, zFl, rFl = side * 11.45, -20.88, 0.38
		binMain:box("gunmetal", xFl, -17.55, -20.78, 1.45, 0.78, 1.26)
		binMain:hollowFlange(Vector3.new(xFl, -17.08, zFl), Vector3.new(0, 1, 0), rFl, 8)
		binMain:hollowPipe("nickel_pipe", xFl, -17.30, zFl, xFl, 12.60, zFl, rFl, rFl * 0.72, 14, true, true)
		local cFlUp = Vector3.new(xFl, 13.55, zFl)
		local _, pFlUp = binMain:hollowElbow90("nickel_pipe", cFlUp, Vector3.new(0, 1, 0), Vector3.new(0, 0, 1), 0.95, rFl, 6, true)
		binMain:hollowPipeVec("nickel_pipe", pFlUp, Vector3.new(xFl, 13.55, -17.55), rFl, rFl * 0.72, 14, true, true)
		binMain:hollowFlange(Vector3.new(xFl, 13.55, -18.08), Vector3.new(0, 0, 1), rFl, 8)
		for _, yfS in ipairs({-13.5, -8.0, -2.5, 3.0, 8.5}) do
			binMain:box("clamp", xFl, yfS, -21.18, 1.18, 0.42, 0.44)
			binMain:hollowPipeVec("cryo_band", Vector3.new(xFl, yfS + 1.8, zFl), Vector3.new(xFl, yfS + 2.15, zFl), rFl * 1.10, rFl * 1.01, 14, true, true, "gunmetal")
		end

		local xBus = side * 13.65
		binMain:box("gunmetal", xBus, -17.52, -20.88, 1.78, 0.80, 1.00)
		binMain:box("gunmetal", xBus,  13.45, -20.88, 1.78, 0.90, 1.04)
		binMain:hollowPipe("conduit_blu", xBus, 13.55, -20.32, xBus, 13.55, -17.60, 0.18, 0.12, 10, true, true)
		binMain:box("hv_tray", xBus, -2.10, -21.24, 1.42, 30.50, 0.32)
		binMain:box("clamp",   xBus, -2.10, -21.01, 1.26, 30.40, 0.08)
		for _, xb in ipairs({{-0.36, "conduit_blu"}, {0.0, "conduit_slv"}, {0.36, "conduit_blu"}}) do
			binMain:hollowPipe(xb[2], xBus + xb[1], -17.30, -20.85, xBus + xb[1], 13.10, -20.85, 0.085, 0.058, 8, false, false)
		end
		for _, ybT in ipairs({-11.0, -3.0, 5.0}) do
			binMain:box("caution", xBus, ybT, -20.90, 1.46, 0.34, 0.08)
		end
	end

	-- Arka ızgaralar üstü kriyojenik plenum köprü borusu + ARKA DIŞ DUVARDA KONDENSER PLENUMUNA TAM İNİŞ HATTI!
	binMain:hollowPipe("nickel_pipe", -16.55, 13.85, 18.55, 16.55, 13.85, 18.55, 0.38, 0.27, 16, true, true)
	for _, xTie in ipairs({-9.5, 0.0, 9.5}) do
		binMain:hollowFlange(Vector3.new(xTie, 13.85, 18.55), Vector3.new(1, 0, 0), 0.38, 8)
		binMain:box("clamp", xTie, 14.38, 18.55, 0.46, 0.96, 0.92)
	end
	-- Arka ızgaraların DIŞ arka yüzünü sızdırmaz kapatan davlumbazlar (Y_src = 16.22..17.88 -> REV05 ile %0 çakışma!)
	for _, sgnG in ipairs({-1, 1}) do
		local xGr = sgnG * 13.15
		binMain:box("gunmetal", xGr, 17.05, 6.20, 9.40, 1.65, 19.60)
		for _, zRibG in ipairs({-1.5, 3.6, 8.7, 13.8}) do
			binMain:box("clamp", xGr, 18.02, zRibG, 9.65, 0.22, 0.42)
		end
		binMain:hollowFlange(Vector3.new(sgnG * 10.60, 17.95, 2.40), Vector3.new(0, 1, 0), 0.62, 10)
		local _, pGrOut = binMain:hollowElbow90("nickel_pipe", Vector3.new(sgnG * 10.60, 21.80, 2.40), Vector3.new(0, 1, 0), Vector3.new(-sgnG, 0, 0), 1.35, 0.62, 7, true)
		binMain:hollowPipeVec("nickel_pipe", Vector3.new(sgnG * 10.60, 17.85, 2.40), Vector3.new(sgnG * 10.60, 20.45, 2.40), 0.62, 0.45, 16, true, true)
		local _, pGrRear = binMain:hollowElbow90("nickel_pipe", Vector3.new(sgnG * 7.85, 21.80, 2.40), Vector3.new(-sgnG, 0, 0), Vector3.new(0, 1, 0), 1.20, 0.62, 7, true)
		binMain:hollowPipeVec("nickel_pipe", pGrOut, Vector3.new(sgnG * 9.05, 21.80, 2.40), 0.62, 0.45, 16, true, true)
		binMain:hollowPipeVec("nickel_pipe", pGrRear, Vector3.new(sgnG * 7.85, 28.40, 2.40), 0.62, 0.45, 16, true, true)
		local _, pGrIn = binMain:hollowElbow90("nickel_pipe", Vector3.new(sgnG * 7.85, 29.55, 2.40), Vector3.new(0, 1, 0), Vector3.new(-sgnG, 0, 0), 1.15, 0.62, 7, true)
		binMain:hollowPipeVec("nickel_pipe", pGrIn, Vector3.new(sgnG * 6.35, 29.55, 2.40), 0.62, 0.45, 16, true, true)
		binMain:hollowFlange(Vector3.new(sgnG * 6.72, 29.55, 2.40), Vector3.new(-sgnG, 0, 0), 0.62, 10)
	end
	-- Üst köprü borusundan (±5.15) içeride Z=14.15'e inip çelik arka duvardan zırhlı boğazla çıkarak
	-- Kondenser Plenum tavanına flanşla bağlanan çift kriyojenik hat (çatı üstüne taşma %0!)
	for _, sgnP in ipairs({-1, 1}) do
		local xP = sgnP * 5.15
		local rP = 0.32
		binMain:hollowFlange(Vector3.new(xP, 13.85, 18.55), Vector3.new(0, 0, -1), rP, 6)
		binMain:hollowPipe("slate_pipe", xP, 13.85, 18.55, xP, 13.85, 14.95, rP, rP * 0.72, 14, true, true)
		local _, pThruWall = binMain:hollowElbow90("slate_pipe", Vector3.new(xP, 13.85, 14.15), Vector3.new(0, 0, -1), Vector3.new(0, 1, 0), 0.80, rP, 6, true)
		binMain:box("gunmetal", xP, 15.55, 14.15, 1.15, 1.35, 1.15) -- Zırhlı arka duvar geçiş sandığı!
		binMain:hollowPipeVec("slate_pipe", pThruWall, Vector3.new(xP, 16.35, 14.15), rP, rP * 0.72, 14, true, true)
		local _, pDownStart = binMain:hollowElbow90("slate_pipe", Vector3.new(xP, 17.15, 14.15), Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), 0.80, rP, 6, true)
		binMain:hollowPipeVec("slate_pipe", pDownStart, Vector3.new(xP, 17.15, 9.35), rP, rP * 0.72, 14, true, true)
		binMain:box("clamp", xP, 16.55, 11.6, 0.85, 1.05, 0.36)
		local _, pRearRun = binMain:hollowElbow90("slate_pipe", Vector3.new(xP, 17.15, 8.55), Vector3.new(0, 0, -1), Vector3.new(0, 1, 0), 0.80, rP, 6, true)
		binMain:hollowPipeVec("slate_pipe", pRearRun, Vector3.new(xP, 27.95, 8.55), rP, rP * 0.72, 14, true, true)
		local _, pPlenumDrop = binMain:hollowElbow90("slate_pipe", Vector3.new(xP, 28.75, 8.55), Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), 0.80, rP, 6, true)
		binMain:hollowPipeVec("slate_pipe", pPlenumDrop, Vector3.new(xP, 28.75, 7.35), rP, rP * 0.72, 14, true, true)
		binMain:hollowFlange(Vector3.new(xP, 28.75, 7.68), Vector3.new(0, 0, -1), rP, 8) -- Kondenser tavan boğaz flanşı!
	end

	binMain:emitToModel(mPiping, "COOLANT_PIPING_RING")
end

-- ============================================================================
-- 4. MODEL M12 — 6 PİSTON ARKASI BAĞLANTILI HİDROLİK SERVİS GALERİSİ
--    (%0 kesik boru, %100 düz MAINT-BAY yazısı, piston taban kaideleri & dış manşon!)
-- ============================================================================
local bayLights = {} -- { {tag=..., lights={pt1, pt2}} }

local BAY_SITES = {
	-- Kademeli teleskopik dış manşon (extCollar): REV02 kayar kapı cebi (27.72) ve CROWN_DECK (24.26) DIŞINDA kalır (%0 Z-fight!)
	{tag = "UPPER",       code = "SL-00", dir = Vector3.new( 0.00, 0,  1.00), rMount = 24.50, extCollar = 3.45},
	{tag = "LEFT",        code = "SL-01", dir = Vector3.new(-1.00, 0,  0.00), rMount = 24.50, extCollar = 0.68},
	{tag = "RIGHT",       code = "SL-02", dir = Vector3.new( 1.00, 0,  0.00), rMount = 24.50, extCollar = 0.68},
	{tag = "LOWER_LEFT",  code = "SL-03", dir = Vector3.new(-0.72, 0, -0.694),rMount = 27.60, extCollar = 3.05},
	{tag = "LOWER_RIGHT", code = "SL-04", dir = Vector3.new( 0.72, 0, -0.694),rMount = 27.60, extCollar = 3.05},
	{tag = "LOWER",       code = "SL-05", dir = Vector3.new( 0.00, 0, -1.00), rMount = 24.50, extCollar = 3.45},
}

local mBaysShared = makeSubModel(staticRoot, "PISTON_REAR_SERVICE_BAYS_01")
local sharedBayBin = MeshBin.new()

local function buildServiceBay(site, bin)
	local d = site.dir.Unit
	local inward = -d
	-- Tüm yatay/çapraz galerilerde (SL-01..SL-04) zAx HER ZAMAN YUKARI (+Z_src / +Y_studio) bakar!
	-- Böylece SL-02 ve SL-04'te yürüyüş ızgarası tavana dönmez ve yazılar asla baş aşağı olmaz!
	local yAx, zAx
	if math.abs(inward.Z) < 0.95 then
		local upSrc = Vector3.new(0, 0, 1)
		yAx = upSrc:Cross(inward).Unit
		zAx = inward:Cross(yAx).Unit
	elseif inward.Z < 0 then
		-- UPPER (SL-00): tavan galerisi, yukarı yönü kontrol odası (+Z_studio = -Y_src)
		zAx = Vector3.new(0, -1, 0)
		yAx = zAx:Cross(inward).Unit
	else
		-- LOWER (SL-05): taban galerisi, yukarı yönü arka duvar (-Z_studio = +Y_src)
		zAx = Vector3.new(0, 1, 0)
		yAx = zAx:Cross(inward).Unit
	end

	local originSrc = Vector3.new(0, -2.70, 0) + d * site.rMount
	local R = CFrame.fromMatrix(originSrc, inward, yAx, zAx)

	local mBay = makeSubModel(mBaysShared, "PISTON_REAR_SERVICE_BAY_" .. site.tag)
	mBay:SetAttribute("BayCode", site.code)

	local function lp(lx, ly, lz)
		return R:PointToWorldSpace(Vector3.new(lx, ly, lz))
	end
	local function lDir(vx, vy, vz)
		return R:VectorToWorldSpace(Vector3.new(vx, vy, vz))
	end
	local function pBox(matKey, lx, ly, lz, sx, sy, sz)
		local w = lp(lx, ly, lz)
		bin:box(matKey, w.X, w.Y, w.Z, sx, sy, sz, R.Rotation)
	end
	local function pRod(matKey, x0, y0, z0, x1, y1, z1, r, segs)
		bin:cylVec(matKey, lp(x0, y0, z0), lp(x1, y1, z1), r, segs or 10, false, true)
	end
	local function pHollowPipe(matKey, x0, y0, z0, x1, y1, z1, rOut, segs)
		bin:hollowPipeVec(matKey, lp(x0, y0, z0), lp(x1, y1, z1), rOut, rOut * 0.72, segs or 14, true, true)
	end

	local LX_FRONT, LX_REAR = -3.32, -38.80
	local LY_IN, LZ_IN, WALL_T = 6.45, 5.75, 0.58
	local vLen = LX_FRONT - LX_REAR
	local vXc  = 0.5 * (LX_FRONT + LX_REAR)

	-- A) Ön sızdırmaz boğaz çerçevesi + KADEMELİ TELESKOPİK DIŞ MANŞON (%0 dış boşluk & %0 eş-düzlemli çakışma!)
	local apY, apZ = 6.05, 4.45
	local outY, outZ = 7.45, 5.08
	local lxC, lxT = -2.92, 0.68
	pBox("gunmetal", lxC, -(apY + outY) * 0.5, 0, lxT, outY - apY, outZ * 2)
	pBox("gunmetal", lxC,  (apY + outY) * 0.5, 0, lxT, outY - apY, outZ * 2)
	pBox("gunmetal", lxC, 0, -(apZ + outZ) * 0.5, lxT, apY * 2, outZ - apZ)
	pBox("gunmetal", lxC, 0,  (apZ + outZ) * 0.5, lxT, apY * 2, outZ - apZ)
	pBox("flange", lxC + 0.44, -apY - 0.14, 0, 0.14, 0.28, apZ * 2 + 0.56)
	pBox("flange", lxC + 0.44,  apY + 0.14, 0, 0.14, 0.28, apZ * 2 + 0.56)
	pBox("flange", lxC + 0.44, 0, -apZ - 0.14, 0.14, apY * 2, 0.28)
	pBox("flange", lxC + 0.44, 0,  apZ + 0.14, 0.14, apY * 2, 0.28)

	-- Kademeli teleskopik dış manşon (+0.66 stud dışa basamaklı -> galeri duvarlarıyla ve kapı cebiyle %0 Z-fight!)
	local extL = site.extCollar or 1.2
	local extXc = LX_FRONT + extL * 0.5
	local LY_EXT, LZ_EXT = LY_IN + WALL_T + 0.08, LZ_IN + WALL_T + 0.08
	pBox("gunmetal", extXc, 0,  LZ_EXT + WALL_T * 0.5, extL, (LY_EXT + WALL_T) * 2, WALL_T)
	pBox("gunmetal", extXc, 0, -LZ_EXT - WALL_T * 0.5, extL, (LY_EXT + WALL_T) * 2, WALL_T)
	for _, sgnY in ipairs({-1, 1}) do
		pBox("gunmetal", extXc, sgnY * (LY_EXT + WALL_T * 0.5), 0, extL, WALL_T, LZ_EXT * 2)
	end

	-- B) Çok tonlu zırhlı tavan, taban, yan duvarlar & arka zırhlı duvar (%0 köşe çakışması!)
	pBox("vault_upper", vXc, 0,  LZ_IN + WALL_T * 0.5, vLen, (LY_IN + WALL_T) * 2, WALL_T)
	pBox("vault_lower", vXc, 0, -LZ_IN - WALL_T * 0.5, vLen, (LY_IN + WALL_T) * 2, WALL_T)
	for _, sgnY in ipairs({-1, 1}) do
		local wy = sgnY * (LY_IN + WALL_T * 0.5)
		pBox("vault_upper", vXc, wy,  3.85, vLen, WALL_T, 3.80)
		pBox("vault_mid",   vXc, wy,  0.00, vLen, WALL_T, 3.86)
		pBox("vault_lower", vXc, wy, -3.85, vLen, WALL_T, 3.80)
		pBox("caution", vXc, sgnY * (LY_IN - 0.09), -1.92, vLen - 1.2, 0.06, 0.18)
	end
	pBox("vault_mid", LX_REAR - WALL_T * 0.5, 0, 0, WALL_T, (LY_IN + WALL_T) * 2, (LZ_IN + WALL_T) * 2)
	-- Arka duvarın DIŞ yüzünde kademeli zırh plakası ve kapalı kollektör kutusu (%0 çakışma!)
	pBox("gunmetal", LX_REAR - WALL_T - 0.62, 0, 1.85, 1.04, 10.60, 5.40)
	for _, ryExt in ipairs({-4.8, 0.0, 4.8}) do
		pBox("clamp", LX_REAR - WALL_T - 1.24, ryExt, 0, 0.16, 0.48, (LZ_IN + WALL_T) * 2 - 0.4)
	end

	-- Arka bağlantılı tesis bakım hava kilidi kapısı (MAINT-BAY — her katman 0.04+ stud ayrık!)
	pBox("clamp", LX_REAR + 0.09, 0, -1.15, 0.14, 5.40, 7.20)
	pBox("dark",  LX_REAR + 0.21, 0, -1.15, 0.08, 4.70, 6.50)
	for _, sgnD in ipairs({-1, 1}) do
		pBox("slate_pipe", LX_REAR + 0.32, sgnD * 1.14, -1.15, 0.10, 2.22, 6.26)
		pBox("flange",     LX_REAR + 0.41, sgnD * 0.16, -1.15, 0.06, 0.14, 6.18)
		pBox("dark",       LX_REAR + 0.42, sgnD * 1.14,  0.45, 0.06, 1.10, 1.55)
	end
	pBox("status_cyan", LX_REAR + 0.23, 0, 2.65, 0.08, 2.40, 0.24)

	-- Dünya-içi %100 DÜZ VE OKUNAKLI MAINT-BAY tabelası (piston üst kotunun üzerinde lz=4.55, %0 Z-fight!)
	pBox("gunmetal", LX_REAR + 0.14, 0, 4.55, 0.12, 4.20, 0.92)
	do
		local nInSt = toStudioVec(inward.X, inward.Y, inward.Z).Unit
		local upSt  = toStudioVec(zAx.X, zAx.Y, zAx.Z).Unit
		local function addBaySign(partName, lxS, lyS, lzS, wStud, hStud, txt)
			local pw = lp(lxS, lyS, lzS)
			local pSt = toStudioPos(pw.X, pw.Y, pw.Z)
			local signPart = Instance.new("Part")
			signPart.Name = partName
			signPart.Size = Vector3.new(wStud, hStud, 0.04)
			signPart.Transparency = 1
			signPart.Anchored = true; signPart.CanCollide = false; signPart.CanQuery = false; signPart.CanTouch = false
			signPart.CFrame = CFrame.lookAt(pSt, pSt + nInSt, upSt)
			local sgui = Instance.new("SurfaceGui")
			sgui.Face = Enum.NormalId.Front
			sgui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
			sgui.PixelsPerStud = 48
			sgui.LightInfluence = 0.68
			sgui.Brightness = 0.68
			sgui.Parent = signPart
			local lbl = Instance.new("TextLabel")
			lbl.Size = UDim2.fromScale(0.94, 0.84)
			lbl.Position = UDim2.fromScale(0.03, 0.08)
			lbl.BackgroundTransparency = 1
			lbl.Font = Enum.Font.Code
			lbl.Text = txt
			lbl.TextColor3 = Color3.fromRGB(218, 232, 246)
			lbl.TextScaled = true
			lbl.Parent = sgui
			signPart.Parent = mBay
		end
		addBaySign("MAINT_AIRLOCK_SIGN_" .. site.code, LX_REAR + 0.26, 0, 4.55, 4.0, 0.78, "MAINT-BAY // " .. site.code)
		addBaySign("PISTON_HYD_SIGN_" .. site.code, -33.54, 0, 1.55, 3.4, 0.62, "HYD-DRIVE // " .. site.code)
	end

	-- C) 6 adet derinlik perspektifi oluşturan kutu-profil taşıyıcı kemer (%0 Z-fight!)
	for _, rx in ipairs({-6.2, -11.8, -17.4, -23.0, -28.6, -34.2}) do
		for _, sgnY in ipairs({-1, 1}) do
			pBox("clamp",  rx, sgnY * (LY_IN - 0.28), 0, 0.52, 0.54, LZ_IN * 2 - 1.06)
			pBox("flange", rx, sgnY * (LY_IN - 0.62), 0, 0.20, 0.08, LZ_IN * 2 - 1.40)
			pRod("clamp", rx, sgnY * (LY_IN - 0.3), LZ_IN - 1.6, rx, sgnY * (LY_IN - 1.8), LZ_IN - 0.3, 0.16, 8)
		end
		for _, sgnZ in ipairs({-1, 1}) do
			pBox("clamp", rx, 0, sgnZ * (LZ_IN - 0.26), 0.52, LY_IN * 2, 0.50)
		end
	end

	-- D) TAM KAPALI DEVRE TAVAN KRİYOJENİK BORULARI + ÇİFT AKÜMÜLATÖR + ÖN/ARKA KOLLEKTÖRLER (%0 kesik boru!)
	for _, sgnY in ipairs({-1, 1}) do
		local pyTop = sgnY * 3.95
		local pzTop = 4.05
		local rTop  = 0.44
		-- 1) Üst boru artık havada kesilmez! Arka duvardaki flanştan (-38.80) tüm tavan boyunca ilerleyip
		--    ön boğaz kollektör sandığına (-4.10) girer ve -7.30'dan aşağı akümülatör ön ağzına bağlanır!
		bin:hollowFlange(lp(LX_REAR + 0.25, pyTop, pzTop), lDir(1, 0, 0), rTop, 8)
		pHollowPipe("nickel_pipe", LX_REAR + 0.05, pyTop, pzTop, -4.15, pyTop, pzTop, rTop, 16)
		pBox("gunmetal", -4.05, sgnY * 4.55, 3.85, 0.85, 2.20, 1.55) -- Ön boğaz üst kollektör kutusu
		for _, fx in ipairs({-13.5, -21.5, -30.5}) do
			bin:hollowFlange(lp(fx, pyTop, pzTop), lDir(1, 0, 0), rTop, 8)
			pBox("clamp", fx, pyTop, 4.92, 0.38, 0.92, 1.15)
		end

		-- 2) Yan Hidrolik Akümülatör Tüpleri (Üst z=1.55 ve Alt z=-0.55) — ön VE arka uçları %100 bağlı!
		local ay = sgnY * 5.38
		pHollowPipe("nickel_pipe", -8.20, ay,  1.55, -27.80, ay,  1.55, 0.50, 16)
		pHollowPipe("slate_pipe",  -8.20, ay, -0.55, -27.80, ay, -0.55, 0.38, 14)
		for _, az in ipairs({1.55, -0.55}) do
			local ar = az > 0 and 0.50 or 0.38
			bin:hollowFlange(lp(-8.20,  ay, az), lDir(1, 0, 0), ar, 8)
			bin:hollowFlange(lp(-27.80, ay, az), lDir(1, 0, 0), ar, 8)
			for _, bx in ipairs({-10.5, -16.0, -21.5, -26.0}) do
				bin:hollowPipeVec("cryo_band", lp(bx - 0.18, ay, az), lp(bx + 0.18, ay, az), ar * 1.10, ar * 1.01, 14, true, true, "gunmetal")
				pBox("clamp", bx, sgnY * 5.88, az, 0.34, 0.98, ar * 2.15)
			end
		end

		-- Üst akümülatör ÖN ucu (-8.20, ay, 1.55) -> Tavan ana borusuna (-7.35, pyTop, pzTop) içi delik dirsekli bağlantı!
		pBox("gunmetal", -7.55, ay, 1.55, 1.30, 1.18, 1.18) -- Akümülatör ön manifold başlığı
		pHollowPipe("conduit_slv", -7.55, ay, 2.05, -7.55, ay, 3.55, 0.24, 12)
		local _, pToTop = bin:hollowElbow90("conduit_slv", lp(-7.55, ay, pzTop), lDir(0, 0, 1), lDir(0, -sgnY, 0), 0.50, 0.24, 6, true)
		bin:hollowPipeVec("conduit_slv", pToTop, lp(-7.55, pyTop, pzTop), 0.24, 0.17, 12, true, true)

		-- Alt akümülatör ÖN ucu (-8.20, ay, -0.55) -> Yan duvar manometre & vana kollektör bloğuna (-7.55, ay, -2.15) dikey iniş!
		pBox("gunmetal", -7.55, ay, -0.55, 1.25, 1.02, 1.02)
		pHollowPipe("slate_pipe", -7.55, ay, -0.95, -7.55, ay, -2.05, 0.24, 12)
		pBox("gunmetal", -8.35, sgnY * 5.65, -2.35, 2.35, 1.05, 1.75) -- Yan vana/manometre manifold dolabı
		pHollowPipe("slate_pipe", -7.15, sgnY * 5.65, -2.35, -3.70, sgnY * 5.65, -2.35, 0.22, 12) -- Ön boğaz duvarına giriş!
		bin:pressureGauge(lp(-7.10, sgnY * 5.45, -1.95), lDir(1, 0, 0))
		pBox("status_cyan", -7.15, sgnY * 5.42, -2.75, 0.08, 0.42, 0.18)

		-- Akümülatör ARKA uçları (-27.80) -> Hem piston arka gövdesine hem arka duvar kollektör dolabına (-38.10) tam bağlantı!
		pBox("gunmetal", -38.05, sgnY * 4.85, 0.35, 1.35, 2.25, 4.45) -- Arka duvar yan hidrolik pompa dolabı
		pHollowPipe("conduit_slv", -27.80, ay,  1.55, -37.55, ay,  1.55, 0.28, 12)
		pHollowPipe("slate_pipe",  -27.80, ay, -0.55, -37.55, ay, -0.55, 0.24, 12)
		local _, pIn = bin:hollowElbow90("conduit_slv", lp(-32.60, ay, 1.55), lDir(-1, 0, 0), lDir(0, -sgnY, 0), 0.72, 0.22, 6, true)
		bin:hollowPipeVec("conduit_slv", pIn, lp(-32.60, sgnY * 2.55, 1.55), 0.22, 0.16, 12, true, true)
		bin:hollowFlange(lp(-32.60, sgnY * 2.68, 1.55), lDir(0, -sgnY, 0), 0.24, 6)
	end

	-- E) LAZER / PİSTON TELESKOPİK GÖVDESİ (REACTOR_PISTON_GUIDE_01) ARKA TAŞIYICI KAİDELERİ,
	--    4 KÖŞE RAY UZATMASI (BRACKETS__frame lx=-31.53 kesik uçlarını arka duvara bağlar!) & ARKA HİDROLİK KÜTÜĞÜ!
	for _, pxSaddle in ipairs({-22.4, -27.8, -33.1}) do
		pBox("gunmetal", pxSaddle, 0, -3.78, 1.15, 5.45, 2.42)
		pBox("flange",   pxSaddle, 0, -2.62, 1.38, 5.75, 0.26)
		for _, sgnS in ipairs({-1, 1}) do
			pBox("clamp", pxSaddle, sgnS * 2.45, -3.80, 1.42, 0.56, 2.46)
		end
	end
	-- BRACKETS__frame 4 köşe sekizgen kılavuz rayının (-31.53, ±3.08, ±3.08) kesik uçlarını
	-- flanşlı manşonlarla yakalayıp arka zırhlı duvara (-38.80) tam bağlayan 4 çelik ankraj kolonu!
	for _, syR in ipairs({-1, 1}) do
		for _, szR in ipairs({-1, 1}) do
			local ryC, rzC = syR * 3.06, szR * 3.06
			pBox("gunmetal", -31.55, ryC, rzC, 0.92, 0.86, 0.86) -- Kesik ray ucunu %100 yutan flanşlı manşon kutusu!
			pBox("flange",   -31.05, ryC, rzC, 0.16, 0.98, 0.98)
			pHollowPipe("slate_pipe", -31.55, ryC, rzC, LX_REAR + 0.12, ryC, rzC, 0.26, 12)
			pBox("clamp", LX_REAR + 0.24, ryC, rzC, 0.42, 0.96, 0.96) -- Arka duvar ankraj plakası!
		end
	end
	-- Piston arka aynası (-33.00 .. -34.85) + OIL_FEED__bronze (-33.16, z=±2.65) kesik uçlarını yutan manifold + arka borular!
	pBox("gunmetal", -33.95, 0, 0.0, 1.90, 4.55, 4.55)
	pBox("flange",   -32.98, 0, 0.0, 0.22, 4.90, 4.90)
	for _, szO in ipairs({-1, 1}) do
		pBox("gunmetal", -33.25, 0, szO * 2.62, 1.15, 3.85, 0.78) -- OIL_FEED__bronze kesik uç kollektörü!
	end
	for _, sgnH in ipairs({-1, 1}) do
		local yh = sgnH * 3.85
		pHollowPipe("nickel_pipe", -34.15, sgnH * 1.55, 1.35, -34.15, yh, 1.35, 0.26, 12)
		local _, pBack = bin:hollowElbow90("nickel_pipe", lp(-34.15, yh, 1.35), lDir(0, sgnH, 0), lDir(-1, 0, 0), 0.55, 0.26, 6, true)
		bin:hollowPipeVec("nickel_pipe", pBack, lp(LX_REAR + 0.15, yh, 1.35), 0.26, 0.18, 12, true, true)
		bin:hollowFlange(lp(LX_REAR + 0.35, yh, 1.35), lDir(1, 0, 0), 0.26, 6)
	end

	-- F) Gerçek 3B Çubuklu Bakım Yürüyüş Izgarası + Sarı Eşik + Korkuluklar
	pBox("dark", vXc, 0, -5.06, vLen - 1.2, LY_IN * 2 - 0.6, 0.12)
	local gx = -5.2
	while gx >= -37.6 do
		pBox("grate_rib", gx, 0, -4.93, 0.22, LY_IN * 2 - 0.65, 0.10)
		gx -= 0.92
	end
	for _, gy in ipairs({-5.8, -4.7, 4.7, 5.8}) do
		pBox("clamp", vXc, gy, -4.96, vLen - 1.2, 0.22, 0.16)
	end
	for _, cxB in ipairs({-8.5, -14.5, -20.5, -26.5, -32.5, -37.2}) do
		pBox("clamp", cxB, 0, -5.32, 0.38, LY_IN * 2 - 0.4, 0.52)
	end
	for _, sgnY in ipairs({-1, 1}) do
		local ry = sgnY * 4.62
		pBox("caution", -19.20, ry, -4.78, 28.40, 0.08, 0.22)
		pRod("flange", -5.00, ry, -3.35, -33.40, ry, -3.35, 0.055, 8)
		pRod("flange", -5.00, ry, -4.08, -33.40, ry, -4.08, 0.042, 8)
		for _, px in ipairs({-5.2, -10.8, -16.4, -22.0, -27.6, -33.2}) do
			pRod("clamp", px, ry, -4.88, px, ry, -3.32, 0.06, 8)
		end
	end

	-- G) Gömme Şerit Servis Lambaları + Kapak Açıklığına Senkron İçi Aydınlatan PointLight Çifti
	for _, sgnY in ipairs({-1, 1}) do
		local lyL, lzL = sgnY * 4.85, 4.92
		for _, lxSeg in ipairs({-9.2, -18.8, -28.4, -36.0}) do
			pBox("clamp",    lxSeg, lyL, lzL + 0.14, 6.20, 0.56, 0.22)
			pBox("bay_lamp", lxSeg, lyL, lzL,        5.80, 0.28, 0.09)
		end
	end

	local pts = {}
	for idx, lxLt in ipairs({-11.5, -26.5}) do
		local pw = lp(lxLt, 0, 3.6)
		local anchor = Instance.new("Part")
		anchor.Name = "BAY_LIGHT_ANCHOR_" .. idx
		anchor.Size = Vector3.new(0.2, 0.2, 0.2)
		anchor.Transparency = 1
		anchor.Anchored = true; anchor.CanCollide = false; anchor.CanQuery = false; anchor.CanTouch = false
		anchor.CFrame = CFrame.new(toStudioPos(pw.X, pw.Y, pw.Z))
		local pl = Instance.new("PointLight")
		pl.Color = Color3.fromRGB(196, 218, 248)
		pl.Brightness = 0.72
		pl.Range = 25
		pl.Shadows = false
		pl.Parent = anchor
		anchor.Parent = mBay
		pts[#pts + 1] = pl
	end
	bayLights[#bayLights + 1] = {tag = site.tag, lights = pts}
end

for _, site in ipairs(BAY_SITES) do
	buildServiceBay(site, sharedBayBin)
end
sharedBayBin:emitToModel(mBaysShared, "SERVICE_BAYS_ALL")

-- ============================================================================
-- 4B. MODEL M12B — REACTOR_FOREBAY_CONTAINMENT_HALL_01 (%0 GÖKYÜZÜ DELİĞİ!)
--     Kontrol odası panoramik camı (Z_studio = +46.65 / Y_src = -46.65) ile
--     sekizgen reaktör ön zırh duvarı (Z_studio = +18.80 / Y_src = -18.80)
--     arasındaki 28.65-stud ön holün tavan, taban, sağ/sol yan duvar ve kontrol
--     odası birleşim alınlarını çok tonlu nervürlü endüstriyel çelik zırhla kapatır!
--     (Y_src <= -18.20 sınırında bittiği için SL-05 / SL-03 / SL-04'e ASLA değmez!)
-- ============================================================================
local mForebay = makeSubModel(staticRoot, "REACTOR_FOREBAY_CONTAINMENT_HALL_01")
do
	local fb = MeshBin.new()
	-- Starts at Y_F1 = -19.86 (Studio Z = +19.86 .. +48.60) -> 0.06 studs cleanly in front of binDiag (-19.80 -> %0 Z-fight!)
	local Y_F0, Y_F1 = -48.60, -19.86
	local yMid = 0.5 * (Y_F0 + Y_F1)
	local yLen = Y_F1 - Y_F0

	-- 1) Üst Çok Tonlu Nervürlü Zırh Tavanı (her katman 0.08+ stud kademeli ayrık -> %0 Z-fight!)
	fb:box("vault_upper", 0, yMid, 25.55, 73.60, yLen, 1.30) -- 24.90 .. 26.20
	fb:box("gunmetal",    0, -47.90, 19.65, 73.60, 1.25, 10.30) -- yalnız cam üstü dış bölgede (Z_studio = 47.28..48.52)
	for _, yg in ipairs({-22.0, -27.5, -33.0, -38.5, -44.0}) do
		fb:box("clamp",  0, yg, 24.08, 70.20, 0.72, 0.72) -- 23.72 .. 24.44
		fb:box("flange", 0, yg, 23.62, 69.60, 0.34, 0.10) -- 23.57 .. 23.67
	end
	for _, xg in ipairs({-24.0, -12.0, 0.0, 12.0, 24.0}) do
		fb:box("vault_mid", xg, yMid, 24.68, 9.60, yLen - 1.6, 0.24) -- 24.56 .. 24.80
	end

	-- 2) Alt Zırhlı Ön Hol Döşemesi (her katman 0.08+ stud kademeli ayrık!)
	fb:box("vault_lower", 0, yMid, -24.25, 73.60, yLen, 1.30) -- -24.90 .. -23.60
	fb:box("gunmetal",    0, -47.90, -19.40, 73.60, 1.25, 8.20)
	for _, yg in ipairs({-22.0, -27.5, -33.0, -38.5, -44.0}) do
		fb:box("clamp",     0, yg, -23.22, 70.20, 0.68, 0.56) -- -23.50 .. -22.94
		fb:box("grate_rib", 0, yg, -22.84, 67.60, 0.30, 0.10) -- -22.89 .. -22.79
	end

	-- 3) Sol & Sağ 3 Kademeli Endüstriyel Yan Muhafaza Duvarları (X = ±35.80, paneller arası 0.06 stud derz!)
	for _, sx in ipairs({-1, 1}) do
		local xW = sx * 35.80
		fb:box("vault_upper", xW, yMid,  15.20, 1.40, yLen, 19.20) -- +5.60 .. +24.80
		fb:box("vault_mid",   xW, yMid,  -1.10, 1.40, yLen, 13.20) -- -7.70 .. +5.50
		fb:box("vault_lower", xW, yMid, -15.65, 1.40, yLen, 15.70) -- -23.50 .. -7.80
		fb:box("gunmetal", sx * 33.40, -47.90, 0.65, 3.20, 1.25, 48.00)
		for _, yg in ipairs({-22.0, -27.5, -33.0, -38.5, -44.0}) do
			fb:box("clamp",  sx * 34.72, yg, 0.65, 0.60, 0.68, 46.80) -- 34.42 .. 35.02 (duvar iç yüzü 35.10!)
			fb:box("flange", sx * 34.32, yg, 0.65, 0.10, 0.32, 46.20) -- 34.27 .. 34.37
		end
		fb:box("clamp", sx * 34.92, yMid,  5.55, 0.24, yLen - 1.2, 0.36)
		fb:box("clamp", sx * 34.92, yMid, -7.75, 0.24, yLen - 1.2, 0.36)
	end

	-- 4) Dış Çevre Boğaz Yakası (binDiag dış çerçevesinin dışında |X|=37.2, Z=+26.8/-25.5 -> %0 sızıntı & %0 çakışma!)
	fb:box("gunmetal", 0, -19.85,  26.85, 76.00, 1.60, 1.10)
	fb:box("gunmetal", 0, -19.85, -25.55, 76.00, 1.60, 1.10)
	for _, sx in ipairs({-1, 1}) do
		fb:box("gunmetal", sx * 37.20, -19.85, 0.65, 1.20, 1.60, 53.60)
	end

	fb:emitToModel(mForebay, "FOREBAY_HALL")
end

-- ============================================================================
-- 5. ESKİ R5 DIŞ KUTU DÖŞEME/DUVAR KESİŞMELERİNİ TEMİZLE + KONTROL ODASI LENTO
--    MİKRO-DERZLERİNİ SIZDIRMAZ ÇELİK İLE KAPAT (%0 GÖKYÜZÜ KAÇAĞI!)
-- ============================================================================
local function cleanLegacyContainmentSlabs(w)
	if not w then return end
	local cont = w:FindFirstChild("01_CONTAINMENT")
	if cont then
		local hideNames = {
			DARK_CORE_STAGE = true,
			INDUSTRIAL_FLOOR = true,
			RIBBED_CEILING = true,
			LEFT_CONTAINMENT_WALL = true,
			RIGHT_CONTAINMENT_WALL = true,
			BACK_CONTAINMENT_WALL = true,
			CONTAINMENT_PANEL_SEAM = true,
			COLD_BLUE_FLOOR_SERVICE_HAIRLINE = true,
			BOUNDARY_HAZARD_BAND = true,
			OUTER_BLUE_GREY_FACETED_BACKPLATE = true,
			DEEP_REACTOR_ACCESS_BAY = true,
			CONTAINMENT_DANGER_MARKER = true,
			ARMOR_HAZARD_DIAGONAL = true,
			ARMOR_VERTICAL_TRIM = true,
			GIANT_REAR_SAFETY_PANEL = true,
			RECESS_ORANGE_ARMOR = true,
			HAZARD_HATCH = true,
			BACK_PANEL_HAZARD_SHEVRON = true,
			HATCH_VENT_BLADE = true,
			REAR_INNER_LUMINESCENT_TRIM = true,
			MIDNIGHT_BACK_CORE_RECESS = true,
		}
		for _, p in ipairs(cont:GetChildren()) do
			if p:IsA("BasePart") and hideNames[p.Name] then
				p.Transparency = 1
				p.CanQuery = false
				p.CanCollide = false
				p.CastShadow = false
				for _, g in ipairs(p:GetDescendants()) do
					if g:IsA("SurfaceGui") then g.Enabled = false end
				end
			end
		end
	end

	-- Eski R5 03_REACTOR_MACHINE (havada kesilen sahte R5 borular, mavi variller, tavandan sarkan çubuklar,
	-- taban neon halkaları) artık gerçek 3B Faz 2 & Faz 3 içi delik borularla değiştirildiği için gizlenir
	-- (Destroy edilmez; CORE_PROTOCOL_Server referansları bozulmaz!).
	local mach = w:FindFirstChild("03_STAR_REACTOR")
	if mach then
		for _, p in ipairs(mach:GetDescendants()) do
			if p:IsA("BasePart") then
				local n = p.Name
				if n:find("COOLANT_RESERVOIR", 1, true)
					or n:find("RESERVOIR_CYAN_GAUGE", 1, true)
					or n:find("ACTIVE_BLUE_WATER", 1, true)
					or n:find("TANK_PRESSURE_CLAMP", 1, true)
					or n:find("BREAKABLE_BLUE_FEED_PIPE", 1, true)
					or n:find("FRONT_VIEWPORT_COOLANT_RISER", 1, true)
					or n:find("FRONT_RISER_CHROME_BAND", 1, true)
					or n:find("HYDRAULIC_SCRAM_CONTROL_ROD", 1, true)
					or n:find("CONTROL_ROD_VISIBLE_TIP", 1, true)
					or n:find("OVERSIZED_CORE_SUSPENSION_PISTON", 1, true)
					or n:find("HEAVY_REACTOR_FOUNDATION", 1, true)
					or n:find("FOUNDATION_INDUCTION_RING", 1, true)
					or n:find("CORE_FLOOR_HEAT_OUTLINE", 1, true)
					or n:find("REACTOR_REAR_BLUE_VANE", 1, true)
					or n:find("INDIGO_REACTOR_CLOUD", 1, true)
					or n:find("WISPY_BLUE_ELECTRICAL_CRACKLE", 1, true)
					or n:find("DISTANT_BLUE_FLECK", 1, true)
				then
					p:SetAttribute("Faz3Hidden", true)
					p.Transparency = 1
					p.CanQuery = false
					p.CanCollide = false
					p.CastShadow = false
				end
			elseif p:IsA("ParticleEmitter") and p.Name == "BLUE_AND_PURPLE_MOVING_PLASMA" then
				p.Enabled = false
			end
		end
	end

	local srv = w:FindFirstChild("04_REACTOR_SERVICE_CORRIDORS")
	if srv then
		for _, ch in ipairs(srv:GetChildren()) do
			if ch:IsA("BasePart") then
				if ch.Name == "REACTOR_SERVICE_HALL_FLOOR" then
					local sgnX = ch.Position.X < 0 and -1 or 1
					ch.Position = Vector3.new(sgnX * 42.3, 11.06, ch.Position.Z)
				elseif ch.Name == "CONTROL_ROOM_TO_HALL_THRESHOLD" then
					ch.Position = Vector3.new(ch.Position.X, 11.21, ch.Position.Z)
				elseif ch.Name == "EMERGENCY_BUNKER_HARD_FLOOR" then
					ch.Size = Vector3.new(25.0, 1.7, 36.4)
					ch.Position = Vector3.new(0.0, 11.08, 99.8)
				end
			end
		end
	end

	-- Kontrol odası:
	--   1) Zemin seramik karosu (Y_top=12.049) ile FLOOR_LIFT_DARK_RECESS (Y_bot=12.050 -> 0.001 stud!) Z-fight'ını
	--      0.032 stud yukarı kademelendirerek tamamen yok et!
	--   2) Yan/arka kapı üstü 0.5-stud R5 lento mikro-boşluklarını YALNIZ DIŞ DUVAR YÜZEYİNİN DIŞINDAN
	--      (|X| = 32.35 > 31.575, Z = 82.80 > 82.025) kapat (%0 gökyüzü sızıntısı & %0 iç duvar çakışması!)
	local gal = w:FindFirstChild("02_PANORAMIC_CONTROL_ROOM")
	if gal then
		for _, ch in ipairs(gal:GetChildren()) do
			if ch:GetAttribute("Faz3Generated") then
				ch:Destroy()
			elseif ch:IsA("BasePart") then
				if ch.Name == "FLOOR_LIFT_DARK_RECESS" then
					ch.Size = Vector3.new(ch.Size.X, 0.05, ch.Size.Z)
					ch.Position = Vector3.new(ch.Position.X, 12.108, ch.Position.Z)
				elseif ch.Name == "RECESSED_LIFT_EDGE_HAIRLINE" then
					ch.Position = Vector3.new(ch.Position.X, 12.14, ch.Position.Z)
				elseif ch.Name == "SIDE_DOOR_OVERHEAD_LINTEL" then
					local sgnX = ch.Position.X < 0 and -1 or 1
					ch.Size = Vector3.new(1.06, 19.0, 7.96)
					ch.Position = Vector3.new(sgnX * 31.0, 31.0, 66.50)
				elseif ch.Name == "REAR_DOOR_HEADER" then
					ch.Size = Vector3.new(10.46, 11.0, 0.97)
				elseif ch.Name == "CENTRAL_RED_FRAMED_STATUS_LIGHT" then
					ch.Size = Vector3.new(23.0, 0.55, 3.1)
					ch.Position = Vector3.new(0.0, 39.525, 60.0)
				elseif ch.Name == "SIDE_SCROLLING_OPERATIONAL_SCREEN" and ch.Position.X < 0 then
					ch.Size = Vector3.new(8.2, 5.4, 0.08)
				end
			end
		end
		local function addSeal(nm, pos, sz, col)
			local sp = Instance.new("Part")
			sp.Name = nm
			sp.Position = pos
			sp.Size = sz
			sp.Color = col
			sp.Material = Enum.Material.Metal
			sp.Anchored = true
			sp.CanCollide = true
			sp.TopSurface = Enum.SurfaceType.Smooth
			sp.BottomSurface = Enum.SurfaceType.Smooth
			sp:SetAttribute("Faz3Generated", true)
			sp.Parent = gal
		end
		local wallCol = Color3.fromRGB(72, 78, 90)
		for _, sgn in ipairs({-1, 1}) do
			local suf = sgn < 0 and "L" or "R"
			addSeal("FAZ3_CTRL_LINTEL_SEAL_" .. suf, Vector3.new(sgn * 32.35, 31.2, 66.2), Vector3.new(1.0, 21.0, 12.5), wallCol)
			addSeal("FAZ3_CTRL_ROOF_EDGE_" .. suf,   Vector3.new(sgn * 32.65, 41.35, 63.6), Vector3.new(1.8, 1.6, 38.0), wallCol)
		end
		addSeal("FAZ3_CTRL_REAR_HEADER_SEAL",  Vector3.new(0.0, 33.8, 82.80), Vector3.new(14.0, 14.0, 1.0), wallCol)
		addSeal("FAZ3_CTRL_REAR_CORRIDOR_CAP", Vector3.new(0.0, 25.0, 91.50), Vector3.new(16.0, 26.0, 1.4), Color3.fromRGB(38, 43, 52))
	end
end

cleanLegacyContainmentSlabs(world)

-- ============================================================================
-- 6. CANLI 60 HZ SERVİS GALERİSİ AYDINLATMA SÜRÜCÜSÜ
-- ============================================================================
local function glide(t)
	t = math.clamp(t, 0, 1)
	return t * t * (3 - 2 * t)
end

if RunService:IsRunning() then
	RunService.Heartbeat:Connect(function()
		if not world or world.Parent ~= Workspace then
			world = Workspace:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
			if world then cleanLegacyContainmentSlabs(world) end
		end
		local mode = world and world:GetAttribute("ReactorMode") or "COLD"
		local isStartup = (mode == "STARTUP")
		local darkness = (isStartup and world and world:GetAttribute("ReactorPilotDarkness")) or 0
		local darkScale = math.clamp(1.0 - 0.72 * darkness, 0.28, 1.0)

		for _, bl in ipairs(bayLights) do
			local rawG = isStartup
				and (assembly:GetAttribute("ReactorPilotGate_" .. bl.tag) or 0)
				or  (assembly:GetAttribute("LiveGate_" .. bl.tag) or 0)
			local openFrac = glide(rawG)
			local br = (0.06 + 0.72 * openFrac) * darkScale
			for _, pt in ipairs(bl.lights) do
				pt.Brightness = br
			end
		end
	end)
end

assembly:SetAttribute("Faz3PipingAndBaysMounted", true)
assembly:SetAttribute("Faz3ServiceBayCount", 6)
assembly:SetAttribute("Faz3RuptureSpoolCount", 4)
assembly:SetAttribute("Faz3HollowPipeRev", 4)
print(string.format("[FAZ3-REV4] Zero-ZFight + Zero-Skybox Forebay Hall + Hollow-Bore Piping Ring (M11) + 6 Shared-Batch Service Bays (M12) active! (%d static 3D MeshParts)", emittedCount))
