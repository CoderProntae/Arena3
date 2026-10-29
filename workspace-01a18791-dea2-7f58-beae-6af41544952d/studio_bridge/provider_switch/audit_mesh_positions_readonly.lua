-- Read-only geometry transform audit after Roblox Importer rearranged grille banks.
local H=game:GetService("HttpService")
local out={}
for _,root in workspace:GetChildren() do
 if root:IsA("Model") and root.Name:sub(1,8)=="REACTOR_" then
  local cf,sz=root:GetBoundingBox()
  local a={at={cf.Position.X,cf.Position.Y,cf.Position.Z},
   size={sz.X,sz.Y,sz.Z},scale=root:GetScale(),parts={}}
  for _,p in root:GetDescendants() do
   if p:IsA("MeshPart") then
    a.parts[p.Name]={p.Position.X,p.Position.Y,p.Position.Z,
      p.Size.X,p.Size.Y,p.Size.Z}
   end
  end
  out[root.Name]=a
 end
end
return H:JSONEncode(out)
