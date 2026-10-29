local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local Players=game:GetService("Players")
local world=WS:WaitForChild("CORE_PROTOCOL_V2_WORLD")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local staticRoot=assembly:WaitForChild("STATIC")
local moving=assembly:WaitForChild("MOVING")
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local function topModel(inst)
 local cur=inst
 while cur and cur.Parent~=moving and cur.Parent~=staticRoot and cur.Parent~=world and cur.Parent~=WS do cur=cur.Parent end
 return cur
end
local function gName(inst)
 local t=topModel(inst); if not t then return "?" end
 if t.Parent==staticRoot then return "S."..t.Name end
 if t.Parent==world then return "D."..t.Name end
 if t.Parent==moving then return "M."..t.Name end
 return t.Name
end
local parts={}
for _,d in staticRoot:GetDescendants() do if d:IsA("BasePart") and d.Transparency<0.99 then parts[#parts+1]=d end end
local byPair={} local examples={} local total=0
for _,p in parts do
 local tm=topModel(p)
 local op=OverlapParams.new(); op.FilterType=Enum.RaycastFilterType.Exclude
 local fl={tm}; for _,c in chars do fl[#fl+1]=c end
 op.FilterDescendantsInstances=fl; op.MaxParts=48
 for _,hh in WS:GetPartsInPart(p, op) do
  if hh.Transparency<0.99 then
   local g1,g2=gName(p),gName(hh)
   if g1~=g2 and g2:sub(1,2)~="M." then
    total+=1
    local key=g1<g2 and (g1.." <> "..g2) or (g2.." <> "..g1)
    byPair[key]=(byPair[key] or 0)+1
    if #examples<18 and (g2:sub(1,2)=="D." or g1:find("CORE") or g1:find("BULKHEAD") or g1:find("SIDE_WALLS")) then
     examples[#examples+1]=g1.."/"..p.Name.." <> "..g2.."/"..hh.Name
    end
   end
  end
 end
end
local pairList={}
for k,v in pairs(byPair) do pairList[#pairList+1]={pair=k,n=v} end
table.sort(pairList,function(a,b) return a.n>b.n end)
return H:JSONEncode({tested=#parts, total=total, pairs=pairList, examples=examples})
