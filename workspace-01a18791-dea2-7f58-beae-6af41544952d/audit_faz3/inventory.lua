local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local out={gameName=game.Name}
local top={}
for _,c in WS:GetChildren() do top[#top+1]=c.ClassName..":"..c.Name end
out.workspaceTop=top
local worlds=0
for _,c in WS:GetChildren() do if c.Name=="CORE_PROTOCOL_V2_WORLD" then worlds+=1 end end
out.editWorldCopies=worlds
local asm=WS:FindFirstChild("REACTOR_MESH_ASSEMBLY")
out.assemblyFound=asm~=nil
if asm then
 out.emitterModuleCount=asm:GetAttribute("EmitterModuleCount")
 local o=asm:GetAttribute("Origin"); out.origin=o and {o.X,o.Y,o.Z} or nil
 local groups={}
 for _,g in asm:GetChildren() do
  local mp=0; local models={}
  for _,d in g:GetDescendants() do if d:IsA("MeshPart") then mp+=1 end end
  for _,m in g:GetChildren() do
   local c=0; for _,d in m:GetDescendants() do if d:IsA("MeshPart") then c+=1 end end
   models[#models+1]=m.Name.."["..m.ClassName..",mp="..c.."]"
  end
  groups[#groups+1]={name=g.Name,class=g.ClassName,meshParts=mp,children=models}
 end
 out.assemblyGroups=groups
 local allmp=0; for _,d in asm:GetDescendants() do if d:IsA("MeshPart") then allmp+=1 end end
 out.assemblyMeshParts=allmp
end
local function scriptList(parent)
 local t={}
 if not parent then return t end
 for _,c in parent:GetChildren() do
  local ok,len=pcall(function() return #c.Source end)
  t[#t+1]=c.ClassName..":"..c.Name.."(len="..(ok and len or -1)..")"
 end
 return t
end
out.serverScripts=scriptList(game:GetService("ServerScriptService"))
out.starterScripts=scriptList(game:GetService("StarterPlayer"):FindFirstChild("StarterPlayerScripts"))
local ss=game:GetService("ServerStorage"):GetChildren()
local sst={} for _,c in ss do sst[#sst+1]=c.ClassName..":"..c.Name end
out.serverStorage=sst
return H:JSONEncode(out)
