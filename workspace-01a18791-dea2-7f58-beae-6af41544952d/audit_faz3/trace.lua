local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local Players=game:GetService("Players")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function trace(o, dir, total)
 local hits={} local pos=o local left=total
 for i=1,14 do
  local params=RaycastParams.new()
  params.FilterType=Enum.RaycastFilterType.Exclude
  params.FilterDescendantsInstances=chars
  params.IgnoreWater=true
  local hit=WS:Raycast(pos, dir*left, params)
  if not hit then hits[#hits+1]="ESCAPE(kalan "..math.floor(left)..")" break end
  local d=(hit.Position-pos).Magnitude
  hits[#hits+1]=string.format("%.1f stud -> %s (T=%.2f) @%s", (total-left)+d, hit.Instance:GetFullName(), hit.Instance:IsA("BasePart") and hit.Instance.Transparency or -1, tostring(hit.Position))
  left-=(d+0.06); pos=hit.Position+dir*0.06
  if left<=0 then hits[#hits+1]="(mesafe doldu)" break end
 end
 return hits
end
local out={}
out.fanThrough=trace(Vector3.new(0,28.3,-4), Vector3.new(0,0,-1), 70)
out.fanThroughOffset=trace(Vector3.new(2.5,30.5,-4), Vector3.new(0,0,-1), 70)
out.floorSlot=trace(Vector3.new(0,30,13), Vector3.new(0,-1,0), 60)
out.plenumBack=trace(Vector3.new(4,31,-26), Vector3.new(1,0,0), 60)
-- ince zemin haritasi
local holes={}
for gx=-2,2,0.5 do
 for gz=9,17,0.5 do
  local excl={} for _,c in chars do excl[#excl+1]=c end
  local found=false
  for _=1,24 do
   local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances=excl; params.IgnoreWater=true
   local hit=WS:Raycast(Vector3.new(gx,30,gz), Vector3.new(0,-120,0), params)
   if not hit then break end
   if hit.Instance:IsA("BasePart") and hit.Instance.Transparency>=0.99 then excl[#excl+1]=hit.Instance else found=true break end
  end
  if not found then holes[#holes+1]={gx,gz} end
 end
end
out.floorFineHoles=holes
return H:JSONEncode(out)
