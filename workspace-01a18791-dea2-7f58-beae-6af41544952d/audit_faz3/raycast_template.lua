local H=game:GetService("HttpService")
local WS=game:GetService("Workspace")
local Players=game:GetService("Players")
local asm=WS:FindFirstChild("REACTOR_MESH_ASSEMBLY")
for _,d in asm:GetDescendants() do
 if d:IsA("MeshPart") then d.CollisionFidelity=Enum.CollisionFidelity.PreciseConvexDecomposition; d.CanQuery=true end
end
task.wait(2)
local chars={}
for _,p in Players:GetPlayers() do if p.Character then chars[#chars+1]=p.Character end end
local ORIGINS=__ORIGINS__
local N=600
local results={}
for _,org in ORIGINS do
 local o=Vector3.new(org[1],org[2],org[3])
 local escapes={} local farHits={} local bins={0,0,0,0,0}
 for i=0,N-1 do
  local y=1-(i/(N-1))*2
  local rr=math.sqrt(math.max(0,1-y*y))
  local th=i*2.399963
  local dir=Vector3.new(math.cos(th)*rr,y,math.sin(th)*rr)
  local excl={}
  for _,c in chars do excl[#excl+1]=c end
  local finalHit=nil local finalDist=nil
  for _=1,24 do
   local params=RaycastParams.new()
   params.FilterType=Enum.RaycastFilterType.Exclude
   params.FilterDescendantsInstances=excl
   params.IgnoreWater=true
   local hit=WS:Raycast(o,dir*500,params)
   if not hit then finalHit=nil break end
   if hit.Instance:IsA("BasePart") and hit.Instance.Transparency>=0.99 then
    excl[#excl+1]=hit.Instance
   else
    finalHit=hit finalDist=(hit.Position-o).Magnitude break
   end
  end
  if not finalDist then
   if #excl>24 then bins[1]=bins[1] end
   if #escapes<140 then escapes[#escapes+1]={math.floor(dir.X*100)/100,math.floor(dir.Y*100)/100,math.floor(dir.Z*100)/100,#excl} end
   bins[5]+=0
  else
   local b= finalDist<5 and 1 or finalDist<20 and 2 or finalDist<40 and 3 or finalDist<90 and 4 or 5
   bins[b]+=1
   if finalDist>90 and #farHits<12 then farHits[#farHits+1]={math.floor(finalDist*10)/10, finalHit.Instance:GetFullName()} end
  end
 end
 local escCount=N-(bins[1]+bins[2]+bins[3]+bins[4]+bins[5])
 results[#results+1]={origin=org, bins=bins, escapes=escCount, escapeDirs=escapes, farHits=farHits}
end
return H:JSONEncode({perOrigin=N, results=results})
