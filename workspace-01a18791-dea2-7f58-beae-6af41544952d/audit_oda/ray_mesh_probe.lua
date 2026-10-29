local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local changed={};for _,p in ipairs(a:GetDescendants()) do if p:IsA('MeshPart') and p.Transparency<.95 and not p.CanQuery then changed[#changed+1]={p,p.CanQuery};p.CanQuery=true end end
local ok,result=xpcall(function()
 local params=RaycastParams.new();params.IgnoreWater=true;local exclude={};for _,p in ipairs(game:GetService('Players'):GetPlayers()) do if p.Character then exclude[#exclude+1]=p.Character end end;params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances=exclude
 local samples={};for _,p in ipairs({{0,30,13},{-1,30,13},{1,30,13},{-10,30,0},{10,30,0},{0,30,0},{0,30,18},{0,30,-6}}) do local h=workspace:Raycast(Vector3.new(p[1],p[2],p[3]),Vector3.new(0,-80,0),params);samples[#samples+1]={at=p,hit=h and h.Instance:GetFullName() or 'MISS',y=h and h.Position.Y or nil} end
 local bore={};for _,p in ipairs({{0,28.3,-19},{2,28.3,-19},{-2,28.3,-19},{0,30,-19}}) do local h=workspace:Raycast(Vector3.new(p[1],p[2],p[3]),Vector3.new(0,0,-35),params);bore[#bore+1]={at=p,hit=h and h.Instance:GetFullName() or 'MISS',pos=h and tostring(h.Position) or ''} end
 return game:GetService('HttpService'):JSONEncode({changed=#changed,floor=samples,back=bore})
end,debug.traceback)
for _,t in ipairs(changed) do if t[1].Parent then t[1].CanQuery=t[2] end end
if not ok then error(result) end;return result
