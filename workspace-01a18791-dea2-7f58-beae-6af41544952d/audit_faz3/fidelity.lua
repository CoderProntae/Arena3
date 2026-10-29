local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local asm=WS:FindFirstChild("REACTOR_MESH_ASSEMBLY")
local fid={} local cq={} local cc={}
for _,d in asm:GetDescendants() do
 if d:IsA("MeshPart") then
  local f=tostring(d.CollisionFidelity); fid[f]=(fid[f] or 0)+1
  local q=tostring(d.CanQuery); cq[q]=(cq[q] or 0)+1
  local c=tostring(d.CanCollide); cc[c]=(cc[c] or 0)+1
 end
end
local pivots={}
local moving=asm:FindFirstChild("MOVING")
for _,m in moving:GetChildren() do
 local p=m:GetPivot().Position
 pivots[m.Name]={math.floor(p.X*100)/100, math.floor(p.Y*100)/100, math.floor(p.Z*100)/100}
end
return H:JSONEncode({fidelity=fid, canQuery=cq, canCollide=cc, movingPivots=pivots})
