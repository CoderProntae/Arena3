local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY')
if not a then return 'ASSEMBLY NOT FOUND' end
local Http=game:GetService('HttpService')
local result={}
for _,root in ipairs(a:GetChildren()) do
 for _,group in ipairs(root:GetChildren()) do
  local c={name=group.Name,root=root.Name,total=0,empty=0,asset=0,other=0}
  for _,m in ipairs(group:GetDescendants()) do
   if m:IsA('MeshPart') then
    c.total+=1
    local id=m.MeshId
    local ok,v=pcall(function() return tostring(m.MeshContent) end)
    if (id=='' or id==nil) and (not ok or v:find('SourceType=None',1,true)) then c.empty+=1
    elseif id~='' then c.asset+=1 else c.other+=1 end
   end
  end
  if c.total>0 then table.insert(result,c) end
 end
end
return Http:JSONEncode(result)
