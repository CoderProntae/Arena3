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
kit.Parent = staticRoot

local V = Vector3.new
buildRupturedSpool(kit, "UPPER_LEFT",  V(-19.95, -8.20, 15.85), V(-19.95, -1.20, 15.85), {2.0, 5.0}, 1101)
buildRupturedSpool(kit, "UPPER_RIGHT", V( 19.95, -8.20, 15.85), V( 19.95, -1.20, 15.85), {2.0, 5.0}, 2202)
buildRupturedSpool(kit, "REAR_LEFT",   V(-19.95, 10.80,  7.80), V(-19.95, 10.80,  1.60), {3.1}, 3303)
buildRupturedSpool(kit, "REAR_RIGHT",  V( 19.95, 10.80,  7.80), V( 19.95, 10.80,  1.60), {3.1}, 4404)

print(string.format("[FAZ4] DAMAGE_PIPE_RUPTURE_KIT_01 kuruldu (%d MeshPart, gizli; 8 agiz ankraji)", emittedCount))
