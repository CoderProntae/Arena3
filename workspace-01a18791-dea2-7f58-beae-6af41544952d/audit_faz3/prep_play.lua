local WS=game:GetService("Workspace")
local a=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local n=0
for _,d in a:GetDescendants() do
 if d:IsA("MeshPart") then d.CollisionFidelity=Enum.CollisionFidelity.PreciseConvexDecomposition d.CanQuery=true n+=1
 elseif d:IsA("BasePart") then d.CanQuery=true end
end
task.wait(3)
return "prep tamam meshpart="..n
