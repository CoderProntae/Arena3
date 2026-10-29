-- Client side companion for the GLB radio; must be mounted to the imported display.
-- Title is taken from the same Sound instance's TrackTitle attribute.
-- Radio/asset permissions and actual Sound playback remain separate from this UI.
local TextService=game:GetService('TextService')
local RunService=game:GetService('RunService')
local RadioDisplay={}
function RadioDisplay.attach(displayPart,sound,opts)
 opts=opts or {};assert(displayPart and displayPart:IsA('BasePart'),'displayPart must be BasePart');assert(sound and sound:IsA('Sound'),'sound must be Sound')
 local speed=tonumber(opts.pixelsPerSecond) or 80;speed=math.clamp(speed,10,400)
 local prior=displayPart:FindFirstChild('AEGIS_RADIO_DISPLAY');if prior then prior:Destroy() end
 local ui=Instance.new('SurfaceGui');ui.Name='AEGIS_RADIO_DISPLAY';ui.Face=opts.face or Enum.NormalId.Front;ui.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;ui.CanvasSize=Vector2.new(1600,240);ui.LightInfluence=0;ui.Parent=displayPart
 local viewport=Instance.new('Frame');viewport.Name='Viewport';viewport.Size=UDim2.fromScale(1,1);viewport.BackgroundColor3=Color3.fromRGB(6,8,30);viewport.BorderSizePixel=0;viewport.ClipsDescendants=true;viewport.Parent=ui
 local text=Instance.new('TextLabel');text.Name='TrackText';text.BackgroundTransparency=1;text.Position=UDim2.fromOffset(36,0);text.Size=UDim2.fromOffset(1528,240);text.Font=Enum.Font.Code;text.TextSize=96;text.TextXAlignment=Enum.TextXAlignment.Left;text.TextYAlignment=Enum.TextYAlignment.Center;text.TextColor3=Color3.fromRGB(78,104,255);text.Text='RADYO KAPALI';text.Parent=viewport
 local width,total,elapsed,last=0,0,0,nil
 local function refresh()
  local title=sound:GetAttribute('TrackTitle');local name=type(title)=='string' and title:gsub('[%c]',' ') or ''
  local cut=utf8.offset(name,181);if cut then name=string.sub(name,1,cut-1) end
  local playing=sound.Playing or opts.showWhenStopped==true
  local current=not playing and 'RADYO KAPALI' or (name~='' and name or 'PARÇA ADI YOK')
  if current==last then return end;last=current;text.Text=current;elapsed=0
  local measured=TextService:GetTextSize(current,text.TextSize,text.Font,Vector2.new(100000,240));width=measured.X;total=math.max(width,1528);text.Size=UDim2.fromOffset(total,240);text.Position=UDim2.fromOffset(36,0)
 end
 local c1=sound:GetAttributeChangedSignal('TrackTitle'):Connect(refresh);local c2=sound:GetPropertyChangedSignal('Playing'):Connect(refresh)
 local heartbeat=RunService.Heartbeat:Connect(function(dt)
  if width<=1528 then return end
  elapsed+=math.min(dt,.1)
  local pause=1.2;local travel=width+160;local period=pause+travel/speed+pause
  local phase=elapsed%period;local x=36
  if phase>pause then x=36-math.min((phase-pause)*speed,travel) end
  text.Position=UDim2.fromOffset(x,0)
 end)
 refresh()
 return {ui=ui,text=text,refresh=refresh,destroy=function() c1:Disconnect();c2:Disconnect();heartbeat:Disconnect();ui:Destroy() end}
end
return RadioDisplay
