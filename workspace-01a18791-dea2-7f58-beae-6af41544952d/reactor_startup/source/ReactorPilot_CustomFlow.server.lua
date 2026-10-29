--!nonstrict
-- REAL 3D VOLUMETRIC FLOW COMPANION (ZERO 2D PARTICLES / BEAMS)
-- All 2D ParticleEmitters and flat 2D Beams have been permanently retired.
-- Stage 02 pressurized 3D fluid plumes, Stage 02-05 3D chamber hulls,
-- Stage 04-05 3D coaxial energy conduits, and the living 3D fusion star
-- run via real-time 3D EditableMesh geometry synchronized to world state.
local Workspace = game:GetService("Workspace")
local world = Workspace:WaitForChild("CORE_PROTOCOL_V2_WORLD", 60)
if not world then return end
world:SetAttribute("ReactorPilotZero2DEffects", true)
world:SetAttribute("ReactorPilotParticleBudget", 0)
world:SetAttribute("ReactorPilotStockSmokeEmitters", 0)
print("[PILOT 3D FLOW] Zero 2D ParticleEmitter/Beam policy active; 3D EditableMesh engine authoritative.")
