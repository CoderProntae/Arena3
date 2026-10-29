local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local asm=WS:FindFirstChild("REACTOR_MESH_ASSEMBLY")
local items={}
local function r3(x) return math.floor(x*1000+0.5)/1000 end
for _,d in asm:GetDescendants() do
 if d:IsA("BasePart") then
  local path=d:GetFullName()
  local c={d.CFrame:GetComponents()}
  local row={path, d.ClassName}
  for i=1,12 do row[#row+1]=r3(c[i]) end
  row[#row+1]=r3(d.Size.X); row[#row+1]=r3(d.Size.Y); row[#row+1]=r3(d.Size.Z)
  row[#row+1]=r3(d.Transparency)
  items[#items+1]=row
 end
end
return H:JSONEncode({count=#items, items=items})
