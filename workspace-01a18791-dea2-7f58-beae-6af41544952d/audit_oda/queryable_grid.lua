local aa=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local changed={};for _,p in ipairs(aa:GetDescendants()) do if p:IsA('MeshPart') and p.Transparency<.95 and not p.CanQuery then changed[#changed+1]=p;p.CanQuery=true end end;local function scan()
local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local Players=game:GetService("Players")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function castClean(o, dir, dist)
 local excl={}
 for _,c in chars do excl[#excl+1]=c end
 for _=1,24 do
  local params=RaycastParams.new()
  params.FilterType=Enum.RaycastFilterType.Exclude
  params.FilterDescendantsInstances=excl
  params.IgnoreWater=true
  local hit=WS:Raycast(o, dir*dist, params)
  if not hit then return nil end
  if hit.Instance:IsA("BasePart") and hit.Instance.Transparency>=0.99 then excl[#excl+1]=hit.Instance
  else return hit end
 end
 return "exhausted"
end
local holes={} local total=0
for gx=-20,20,2 do
 for gz=-8,44,2 do
  total+=1
  local hit=castClean(Vector3.new(gx,30,gz), Vector3.new(0,-1,0), 120)
  if hit==nil then holes[#holes+1]={gx,gz} end
 end
end
-- tavan: yukari izgara (oda hacmi)
local ceilHoles={}
for gx=-20,20,2 do
 for gz=-8,20,2 do
  local hit=castClean(Vector3.new(gx,20,gz), Vector3.new(0,1,0), 120)
  if hit==nil then ceilHoles[#ceilHoles+1]={gx,gz} end
 end
end
return H:JSONEncode({floorTested=total, floorHoles=holes, ceilHoles=ceilHoles})

end;local ok,res=xpcall(scan,debug.traceback);for _,p in ipairs(changed) do if p.Parent then p.CanQuery=false end end;if not ok then error(res) end;return res