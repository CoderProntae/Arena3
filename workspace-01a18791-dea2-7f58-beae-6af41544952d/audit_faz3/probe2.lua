local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local Players=game:GetService("Players")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function castClean(o, dir, dist)
 local excl={}
 for _,c in chars do excl[#excl+1]=c end
 for _=1,24 do
  local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances=excl; params.IgnoreWater=true
  local hit=WS:Raycast(o, dir*dist, params)
  if not hit then return nil end
  if hit.Instance:IsA("BasePart") and hit.Instance.Transparency>=0.99 then excl[#excl+1]=hit.Instance else return hit end
 end
 return nil
end
local out={}
local sides={}
for _,x in {-1,-0.4,0.4,1} do
 local hit=castClean(Vector3.new(x,30,13), Vector3.new(0,-1,0), 60)
 sides[#sides+1]=string.format("x=%.1f -> %s", x, hit and (hit.Instance:GetFullName().." @"..tostring(hit.Position)) or "ESCAPE")
end
out.floorSides=sides
-- plenum eksen deligi kapsamı: z=-20'den -Z'ye paralel isinlar, eksen etrafi izgara
local bore={}
for dx=-2,2,0.5 do
 for dy=-2,2,0.5 do
  local hit=castClean(Vector3.new(dx,28.3+dy,-19), Vector3.new(0,0,-1), 25)
  if not hit then bore[#bore+1]={dx,dy} end
 end
end
out.boreOpenOffsets=bore
-- arka kapagin eksende ilk vurdugu yer (on yuz)
local capHit=castClean(Vector3.new(3,31,-19), Vector3.new(0,0,-1), 40)
out.rearCapSample=capHit and (capHit.Instance:GetFullName().." @"..tostring(capHit.Position)) or "none"
return H:JSONEncode(out)
