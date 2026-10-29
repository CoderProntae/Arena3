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

-- Temiz idempotensi: yalniz kendi Faz4Generated cocuklarini sil
for _, ch in ipairs(staticRoot:GetChildren()) do
	if ch:GetAttribute("Faz4Generated") then
		ch:Destroy()
	end
end

