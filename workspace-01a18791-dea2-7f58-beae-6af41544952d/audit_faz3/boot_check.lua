local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local out={}
local world=WS:FindFirstChild("CORE_PROTOCOL_V2_WORLD")
out.worldFound=world~=nil
if world then
 out.mode=world:GetAttribute("ReactorMode")
 out.pilotStatus=world:GetAttribute("ReactorPilotStatus")
 out.pilotReady=world:GetAttribute("ReactorPilotReady")
 local folders={}
 for _,c in world:GetChildren() do folders[#folders+1]=c.ClassName..":"..c.Name end
 out.worldChildren=folders
end
local asm=WS:FindFirstChild("REACTOR_MESH_ASSEMBLY")
out.faz2=asm and asm:GetAttribute("Faz2ChamberMounted")
out.faz3=asm and asm:GetAttribute("Faz3PipingAndBaysMounted")
local pcount=0
if world then for _,d in world:GetDescendants() do if d:IsA("BasePart") then pcount+=1 end end end
out.worldBaseParts=pcount
return H:JSONEncode(out)
