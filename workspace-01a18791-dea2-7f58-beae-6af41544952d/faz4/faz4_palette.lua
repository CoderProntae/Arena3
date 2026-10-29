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

