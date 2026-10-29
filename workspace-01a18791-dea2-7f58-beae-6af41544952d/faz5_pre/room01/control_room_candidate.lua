-- AEGIS: control room architectural candidate, non-destructive visual preview.
-- All positions are real studs; existing walls, windows, controls and openings remain.
local world=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',45)
local prior=world:FindFirstChild('PRE5_CONTROL_ROOM_ARCH_CANDIDATE');if prior then prior:Destroy() end
local m=Instance.new('Model');m.Name='PRE5_CONTROL_ROOM_ARCH_CANDIDATE'
local steel=Color3.fromRGB(82,94,108);local dark=Color3.fromRGB(36,46,58);local panel=Color3.fromRGB(151,161,171);local pale=Color3.fromRGB(187,194,198);local blue=Color3.fromRGB(83,162,187)
local function part(name,pos,size,color,mat,trans)
 local p=Instance.new('Part');p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Size=size;p.CFrame=CFrame.new(pos);p.Color=color;p.Material=mat or Enum.Material.Metal;p.Transparency=trans or 0;p.Parent=m;return p
end
-- Six pairs of rear wall cassettes. Door aperture x=-5..5 is untouched.
for _,side in ipairs({-1,1}) do
 for i=0,2 do
  local x=side*(9.1+i*8.3)
  part('REAR_PANEL_BACKING',Vector3.new(x,24.7,80.32),Vector3.new(7.75,20.8,.17),dark)
  part('REAR_UPPER_CASSETTE',Vector3.new(x,29.5,80.18),Vector3.new(7.25,9.8,.16),panel)
  part('REAR_LOWER_CASSETTE',Vector3.new(x,19.1,80.18),Vector3.new(7.25,9.6,.16),steel)
  part('REAR_MID_SEPARATOR',Vector3.new(x,24.42,80.06),Vector3.new(7.7,.22,.14),dark)
  part('REAR_BASE_KICKPLATE',Vector3.new(x,14.6,80.05),Vector3.new(7.7,.55,.14),dark)
  for _,dx in ipairs({-3.7,3.7}) do
   part('REAR_VERTICAL_RAIL',Vector3.new(x+dx,24.7,80.05),Vector3.new(.18,20.7,.16),steel)
   for _,y in ipairs({16,23,32.8}) do part('REAR_RAIL_FASTENER',Vector3.new(x+dx,y,79.94),Vector3.new(.12,.12,.08),pale) end
  end
  for j=0,4 do part('REAR_SERVICE_VENT',Vector3.new(x,20.1+j*.36,80.06),Vector3.new(4.4,.075,.12),dark) end
 end
end
-- Side wall architecture stops on both sides of the 8-stud corridor doors.
for _,side in ipairs({-1,1}) do
 local x=side*30.55;local inner=x-side*.15
 for _,z in ipairs({49.5,54.6,59.7,73.2,78.0}) do
  part('SIDE_PANEL_BACKING',Vector3.new(x,24.7,z),Vector3.new(.16,20.5,4.7),dark)
  part('SIDE_UPPER_CASSETTE',Vector3.new(inner,29.4,z),Vector3.new(.14,9.7,4.3),panel)
  part('SIDE_LOWER_CASSETTE',Vector3.new(inner,19.1,z),Vector3.new(.14,9.6,4.3),steel)
  part('SIDE_MID_SEPARATOR',Vector3.new(inner-side*.10,24.4,z),Vector3.new(.14,.22,4.65),dark)
  part('SIDE_BASE_KICKPLATE',Vector3.new(inner-side*.10,14.6,z),Vector3.new(.14,.55,4.65),dark)
  for _,dz in ipairs({-2.24,2.24}) do part('SIDE_VERTICAL_RAIL',Vector3.new(inner-side*.10,24.7,z+dz),Vector3.new(.16,20.4,.18),steel) end
 end
 -- Subdued, non-emissive color strip, high above exit traffic.
 for _,z in ipairs({54.6,75.6}) do part('SIDE_SERVICE_COLOR_ACCENT',Vector3.new(inner-side*.12,34.3,z),Vector3.new(.10,.10,6.8),blue,Enum.Material.Metal) end
end
m.Parent=world
return game:GetService('HttpService'):JSONEncode({candidate=m.Name,parts=#m:GetChildren(),note='Play-only; no modifications to existing control room'})
