local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local world=WS:WaitForChild("CORE_PROTOCOL_V2_WORLD")
local out={mode=world:GetAttribute("ReactorMode")}
local wbp=0 for _,d in world:GetDescendants() do if d:IsA("BasePart") then wbp+=1 end end
out.worldBaseParts=wbp
local dmg=world:FindFirstChild("06_DAMAGE_THAT_STAYS")
out.damageFolderPresent=dmg~=nil
local names={}
if dmg then for _,d in dmg:GetDescendants() do if d:IsA("BasePart") then names[d.Name]=(names[d.Name] or 0)+1 end end end
local banned={}
for n,c in pairs(names) do
 if n:find("MOLTEN") or n:find("RUPTURE_LIP") or n:find("RISER_PRESSURE") or n:find("CRACK") or n:find("GLAZING") then banned[n]=c end
end
out.bannedLeftovers=banned
local dn=0 for _ in pairs(names) do dn+=1 end
out.damageDistinctNames=dn
local gone={"BROKEN_EMITTER_SHOWER","REAL_BROKEN_PIPE_JET","STEAM_FROM_PRESSURE","VIEWABLE_CYAN_COOLANT_JET","BROKEN_MANIFOLD_BLUE_VAPOR"}
local foundGone={}
for _,d in WS:GetDescendants() do
 for _,g in gone do if d.Name==g then foundGone[#foundGone+1]=g end end
end
out.removedEmittersStillPresent=foundGone
local panes={}
for _,d in world:GetDescendants() do
 if d:IsA("BasePart") and (d.Name:find("PANORAMIC_LAMINATED_GLASS") or d.Name:find("GLASS_MULLION")) then
  panes[#panes+1]={name=d.Name, pos=tostring(d.Position), size=tostring(d.Size), T=d.Transparency, parent=d.Parent and d.Parent.Name}
 end
end
out.glassLive=panes
out.pilotReady=world:GetAttribute("ReactorPilotReady")
out.pilotStatus=world:GetAttribute("ReactorPilotStatus")
return H:JSONEncode(out)
