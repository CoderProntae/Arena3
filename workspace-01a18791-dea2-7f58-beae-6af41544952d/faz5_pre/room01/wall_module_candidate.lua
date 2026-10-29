-- Single architectural part only; separated from room for visual approval.
local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30);local old=w:FindFirstChild('PRE5_CONTROL_ROOM_ARCH_CANDIDATE');if old then old:Destroy() end
local old2=workspace:FindFirstChild('PRE5_WALL_MODULE_SHOWCASE');if old2 then old2:Destroy() end
local container=Instance.new('Model');container.Name='PRE5_WALL_MODULE_SHOWCASE'
local model=Instance.new('Model');model.Name='01_CONTROL_WALL_PANEL_CANDIDATE';model.Parent=container
local function b(n,pos,size,col,mat,parent)
 local p=Instance.new('Part');p.Name=n;p.Size=size;p.CFrame=CFrame.new(pos);p.Color=Color3.fromRGB(unpack(col));p.Material=mat or Enum.Material.Metal;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Parent=parent or model;return p end
local x=150;local centerY=18
b('PANEL_STRUCTURAL_FRAME',Vector3.new(x,centerY,0),Vector3.new(4.4,10.7,.38),{41,51,64})
b('PANEL_UPPER_FACE',Vector3.new(x,20.35,-.23),Vector3.new(4.02,5.4,.16),{170,181,190})
b('PANEL_LOWER_FACE',Vector3.new(x,15.08,-.23),Vector3.new(4.02,4.7,.16),{82,96,109})
b('PANEL_MIDSEAM',Vector3.new(x,17.65,-.34),Vector3.new(4.05,.20,.09),{31,43,55})
b('PANEL_BASE_TRIM',Vector3.new(x,12.90,-.34),Vector3.new(4.05,.28,.09),{41,52,63})
for _,dx in ipairs({-2.11,2.11}) do
 b('EDGE_RAIL',Vector3.new(x+dx,18,-.30),Vector3.new(.12,10.6,.12),{93,108,119})
 for _,y in ipairs({13.15,17.7,22.8}) do local p=b('RECESSED_FASTENER',Vector3.new(x+dx,y,-.38),Vector3.new(.11,.11,.05),{199,205,207});p.Shape=Enum.PartType.Ball end
end
b('VENT_RECESS',Vector3.new(x,15.4,-.33),Vector3.new(2.7,1.15,.06),{39,48,57})
for i=0,4 do b('VENT_FIN',Vector3.new(x,14.95+i*.22,-.38),Vector3.new(2.62,.09,.07),{124,138,146}) end
b('CORNER_MARK',Vector3.new(x-1.58,22.3,-.34),Vector3.new(.38,.055,.05),{98,158,172})
-- Neutral isolated plinth: presentation only, not part of panel.
b('SHOWCASE_PLINTH',Vector3.new(x,12.50,0),Vector3.new(12,.35,8),{33,41,51},Enum.Material.Slate,container)
b('SHOWCASE_BACKDROP',Vector3.new(x,18.2,2),Vector3.new(16,14,.4),{61,70,80},Enum.Material.SmoothPlastic,container)
container.Parent=workspace
return game:GetService('HttpService'):JSONEncode({part=model.Name,componentCount=#model:GetChildren(),scope='single panel, Play-only candidate',roomAdded=false})
