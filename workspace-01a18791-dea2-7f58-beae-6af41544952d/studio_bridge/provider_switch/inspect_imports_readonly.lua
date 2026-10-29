-- READ-ONLY imported GLB audit. Does not change Studio or the camera.
local H=game:GetService("HttpService")
local names={
 "REACTOR_EMITTER_REV03", "REACTOR_CORE_MANYETIK_01",
 "REACTOR_WALL_HATCH_THROUGH_01", "REACTOR_PISTON_GUIDE_01",
 "REACTOR_REAR_SERVICE_GRILLES_01", "REACTOR_REAR_BULKHEAD_IRON_REV04",
 "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02",
}
local function vec(v)
 return {math.round(v.X*1000)/1000,math.round(v.Y*1000)/1000,math.round(v.Z*1000)/1000}
end
local data={place=game.Name, models={}, server_scripts={}}
for _,sc in game.ServerScriptService:GetChildren() do
 data.server_scripts[#data.server_scripts+1]={name=sc.Name,class=sc.ClassName,enabled=sc:IsA("BaseScript") and sc.Enabled or nil}
end
for _,n in names do
 local m=workspace:FindFirstChild(n)
 local info={name=n,exists=m~=nil}
 if m and m:IsA("Model") then
  local bc,bs=m:GetBoundingBox()
  info.bounds={centre=vec(bc.Position),size=vec(bs)}
  local pivot=m:GetPivot()
  info.pivot=vec(pivot.Position)
  info.axes={x=vec(pivot.RightVector),y=vec(pivot.UpVector),z=vec(pivot.LookVector)}
  local sample={};local counts={mesh=0,anchored=0,collision=0,surface=0}
  local group={}
  for _,v in m:GetDescendants() do
   if v:IsA("MeshPart") then
    counts.mesh+=1
    if v.Anchored then counts.anchored+=1 end
    if v.CanCollide then counts.collision+=1 end
    if #sample<2 then
     sample[#sample+1]={name=v.Name,at=vec(v.Position),size=vec(v.Size),
      material=v.Material.Name,tex=(v.TextureID~=""),children=#v:GetChildren()}
    end
    local prefix=v.Name:match("^(HATCH_LEFT)") or v.Name:match("^(HATCH_RIGHT)")
      or v.Name:match("^(STAGE[123])") or v.Name:match("^(PUSHER)")
      or v.Name:match("^(CENTER__WHITE_CORE)")
    if prefix then
     local key=prefix.."_node_count"
     group[key]=(group[key] or 0)+1
     if not group[prefix] then group[prefix]={name=v.Name,at=vec(v.Position),size=vec(v.Size)} end
    end
   elseif v:IsA("SurfaceAppearance") then counts.surface+=1 end
  end
  info.counts=counts;info.sample=sample;info.moving_parts=group
 end
 data.models[#data.models+1]=info
end
return H:JSONEncode(data)
