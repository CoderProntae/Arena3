local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',30);local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30);local st=a:WaitForChild('STATIC',30);local mov=a:WaitForChild('MOVING',30)
local out={static={},moving={},checks={},empty={},worldGroups={},visibleLegacy={}}
local function summary(obj)
 local m,p=0,0;for _,d in ipairs(obj:GetDescendants()) do if d:IsA('MeshPart') then m+=1 elseif d:IsA('BasePart') then p+=1 end end
 return {name=obj.Name,class=obj.ClassName,mesh=m,parts=p}
end
for _,p in ipairs(st:GetChildren()) do table.insert(out.static,summary(p)) end
for _,p in ipairs(mov:GetChildren()) do table.insert(out.moving,summary(p)) end
for _,p in ipairs(w:GetChildren()) do table.insert(out.worldGroups,summary(p)) end
for _,p in ipairs(a:GetDescendants()) do if p:IsA('MeshPart') and p.MeshId=='' and p.MeshContent.SourceType==Enum.ContentSourceType.None then table.insert(out.empty,p:GetFullName()) end end
for _,p in ipairs(w:GetDescendants()) do if p:IsA('BasePart') and p.Transparency<.95 and p.Position.X>-24 and p.Position.X<24 and p.Position.Y>11 and p.Position.Y<48 and p.Position.Z>-18 and p.Position.Z<20 and p.Size.Magnitude>2 then table.insert(out.visibleLegacy,{name=p.Name,path=p:GetFullName(),alpha=p.Transparency,size=tostring(p.Size)}) end end
return game:GetService('HttpService'):JSONEncode(out)
