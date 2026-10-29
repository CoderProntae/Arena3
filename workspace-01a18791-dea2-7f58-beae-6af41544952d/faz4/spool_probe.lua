local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local a=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local out={spoolCountAttr=a:GetAttribute("Faz3RuptureSpoolCount"), spools={}, pipingChildren={}}
for _,d in a:GetDescendants() do
 if d.Name:upper():find("SPOOL") then
  local e={path=d:GetFullName(), class=d.ClassName}
  if d:IsA("BasePart") then e.pos=tostring(d.Position) e.size=tostring(d.Size)
  elseif d:IsA("Model") then e.pivot=tostring(d:GetPivot().Position) local _,sz=d:GetBoundingBox() e.bbox=tostring(sz) end
  local at={} for k,v in d:GetAttributes() do at[#at+1]=k.."="..tostring(v) end e.attrs=at
  out.spools[#out.spools+1]=e
 end
end
local st=a:WaitForChild("STATIC")
local ring=st:FindFirstChild("REACTOR_COOLANT_PIPING_RING_01")
if ring then for _,c in ring:GetChildren() do out.pipingChildren[#out.pipingChildren+1]=c.ClassName..":"..c.Name end end
return H:JSONEncode(out)
