-- Real-time triangular glazing fragments: two wedged solids per triangle.
-- All dimensions here are already world-space studs (UNITS, FRAME), not the
-- authored 0.5-scale compatibility constructors in the gameplay script.
local function spawnNaturalGlass(pane,container,frozen)
 local nx=pane.Size.X>20 and 8 or 3
 local ny=5
 local hx,hy=pane.Size.X*.5,pane.Size.Y*.5
 local nodes={}
 for y=0,ny do
  nodes[y]={}
  for x=0,nx do
   local px=-hx+pane.Size.X*x/nx
   local py=-hy+pane.Size.Y*y/ny
   if x>0 and x<nx then px+=rng:NextNumber(-.27,.27)*pane.Size.X/nx end
   if y>0 and y<ny then py+=rng:NextNumber(-.27,.27)*pane.Size.Y/ny end
   nodes[y][x]=pane.CFrame:PointToWorldSpace(UNITS.new(px,py,0))
  end
 end
 local count=0
 local fragments={}
 local function triangle(a,b,c)
  -- Use longest edge as the base; the perpendicular projection then falls
  -- on that edge, allowing the triangle to be split into two right wedges.
  local ab,ac,bc=b-a,c-a,c-b
  if ab:Dot(ab)>ac:Dot(ac) and ab:Dot(ab)>bc:Dot(bc) then c,a=a,c
  elseif ac:Dot(ac)>bc:Dot(bc) and ac:Dot(ac)>ab:Dot(ab) then a,b=b,a end
  ab,ac,bc=b-a,c-a,c-b
  if bc.Magnitude<.01 then return end
  local normal=ac:Cross(ab)
  if normal.Magnitude<.01 then return end
  local right=normal.Unit;local back=bc.Unit;local up=back:Cross(right).Unit
  local height=math.abs(ab:Dot(up));local w1=math.abs(ab:Dot(back));local w2=math.abs(ac:Dot(back))
  if height<.05 or w1<.05 or w2<.05 then return end
  local parts={}
  local function piece(name,width,cf)
   local p=Instance.new('WedgePart');p.Name=name;p.Size=UNITS.new(.055,height,width);p.CFrame=cf
   p.Material=Enum.Material.SmoothPlastic;p.Color=Color3.fromRGB(185,214,223);p.Transparency=.79
   p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false
   p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth;p.Parent=container
   parts[#parts+1]=p
   return p
  end
  local p1=piece('M14_GLASS_SHARD_A',w1,FRAME.fromMatrix((a+b)*.5,right,up,back))
  local p2=piece('M14_GLASS_SHARD_B',w2,FRAME.fromMatrix((a+c)*.5,-right,up,-back))
  if not frozen then
   local center=(a+b+c)/3
   local impact=UNITS.new(0,26.5,46.62)
   local radial=center-impact
   local radial2=UNITS.new(radial.X,radial.Y,0)
   if radial2.Magnitude<.1 then radial2=UNITS.new(0,1,0) end
   local velocity=radial2.Unit*rng:NextNumber(3,7)+UNITS.new(rng:NextNumber(-1,1),rng:NextNumber(3,7),rng:NextNumber(10,16))
   local spin=UNITS.new(rng:NextNumber(-3,3),rng:NextNumber(-3,3),rng:NextNumber(-3,3))
   local origin=FRAME.new(center)
   fragments[#fragments+1]={origin=origin,velocity=velocity,spin=spin,parts=parts,
    offsets={origin:ToObjectSpace(p1.CFrame),origin:ToObjectSpace(p2.CFrame)}}
  end
  count+=1
 end
 for y=0,ny-1 do for x=0,nx-1 do
  local a,b,c,d=nodes[y][x],nodes[y][x+1],nodes[y+1][x],nodes[y+1][x+1]
  if (x+y)%2==0 then triangle(a,b,c);triangle(b,d,c)
  else triangle(a,b,d);triangle(a,d,c) end
 end end
 if not frozen and #fragments>0 then
  -- One bounded batched animation per pane avoids hundreds of colliding
  -- assemblies while keeping both halves of each shard perfectly attached.
  local elapsed,step=0,0;local con
  con=RunService.Heartbeat:Connect(function(dt)
   if not container.Parent then con:Disconnect();return end
   elapsed+=math.min(dt,.1);step+=dt
   if elapsed>=2.5 then
    con:Disconnect();for _,f in ipairs(fragments) do for _,p in ipairs(f.parts) do p:Destroy() end end
    return
   end
   if step<1/30 then return end;step=0
   local moving,cframes={},{}
   local transparency=elapsed>1.55 and (.79+.21*math.clamp((elapsed-1.55)/.95,0,1)) or .79
   for _,f in ipairs(fragments) do
    local pos=f.origin.Position+f.velocity*elapsed+UNITS.new(0,-9*elapsed*elapsed,0)
    local spin=FRAME.Angles(f.spin.X*elapsed,f.spin.Y*elapsed,f.spin.Z*elapsed)
    local pose=FRAME.new(pos)*spin
    for i,p in ipairs(f.parts) do
     if p.Parent then p.Transparency=transparency;moving[#moving+1]=p;cframes[#cframes+1]=pose*f.offsets[i] end
    end
   end
   if #moving>0 then Workspace:BulkMoveTo(moving,cframes,Enum.BulkMoveMode.FireCFrameChanged) end
  end)
 end
 return count
end
