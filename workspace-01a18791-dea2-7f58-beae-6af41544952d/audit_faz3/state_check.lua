local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local a=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local fid={} local cq=0 local tot=0
for _,d in a:GetDescendants() do
 if d:IsA("MeshPart") then
  fid[d.CollisionFidelity.Name]=(fid[d.CollisionFidelity.Name] or 0)+1
 end
 if d:IsA("BasePart") then tot+=1 if d.CanQuery then cq+=1 end end
end
local mv=a:WaitForChild("MOVING")
local em=mv:FindFirstChild("REACTOR_EMITTER_REV03_LEFT")
local ro=mv:FindFirstChild("REACTOR_REAR_TURBINE_ROTOR")
return H:JSONEncode({fidelity=fid, canQueryTrue=cq, baseParts=tot,
 emitterLeftPivot=em and tostring(em:GetPivot().Position) or "yok",
 rotorPivot=ro and tostring(ro:GetPivot().Position) or "yok",
 editWorld=WS:FindFirstChild("CORE_PROTOCOL_V2_WORLD")~=nil})
