local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local Players=game:GetService("Players")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function transect(o, dir, total)
 local hits={} local pos=o local left=total
 for i=1,20 do
  local params=RaycastParams.new(); params.FilterType=Enum.RaycastFilterType.Exclude; params.FilterDescendantsInstances=chars; params.IgnoreWater=true
  local hit=WS:Raycast(pos, dir*left, params)
  if not hit then hits[#hits+1]="SON" break end
  local d=(hit.Position-pos).Magnitude
  local top=hit.Instance
  local path={}
  local cur=top
  for _=1,4 do if cur then path[#path+1]=cur.Name cur=cur.Parent end end
  hits[#hits+1]=string.format("%.2f %s T=%.2f", (total-left)+d, table.concat(path,"<"), hit.Instance:IsA("BasePart") and hit.Instance.Transparency or -1)
  left-=(d+0.05); pos=hit.Position+dir*0.05
  if left<=0 then break end
 end
 return hits
end
local out={}
out.leftZ=transect(Vector3.new(-36,26.5,14), Vector3.new(0,0,-1), 26)
out.leftY=transect(Vector3.new(-36,40,2.7), Vector3.new(0,-1,0), 26)
out.llZ=transect(Vector3.new(-25.9,1.53,14), Vector3.new(0,0,-1), 26)
out.upperX=transect(Vector3.new(-14,62.47,2.7), Vector3.new(1,0,0), 26)
return H:JSONEncode(out)
