-- Status panel: dynamic Roblox companion for the approved GLB candidate.
-- Do not run until the imported screen face and four lamp MeshParts have been mapped.
-- Data source: the reactor world attributes. No fallback values are fabricated.
local StatusPanel={}
local severityByMode={COLD='standby',STARTUP='startup',ONLINE='normal',WARNING='warning',MELTDOWN='alarm',AFTERMATH='alarm',FAILED_STARTUP='alarm',FREEZEDOWN='warning',SCRAM='shutdown',SUCCESS_SHUTDOWN='shutdown',RESETTING='standby'}
local textByMode={COLD='ATEŞLEME BEKLENİYOR',STARTUP='REAKTÖR BAŞLATILIYOR',ONLINE='REAKTÖR ÇALIŞIYOR',WARNING='UYARI',MELTDOWN='REAKTÖR ERİMESİ',AFTERMATH='KRİTİK HASAR',FAILED_STARTUP='BAŞLATMA BAŞARISIZ',FREEZEDOWN='AŞIRI SOĞUMA',SCRAM='ACİL KAPATMA',SUCCESS_SHUTDOWN='REAKTÖR KAPATILDI',RESETTING='SİSTEM SIFIRLANIYOR'}
local colors={standby=Color3.fromRGB(110,179,205),startup=Color3.fromRGB(90,160,235),normal=Color3.fromRGB(110,210,105),warning=Color3.fromRGB(240,178,43),alarm=Color3.fromRGB(238,58,51),shutdown=Color3.fromRGB(110,179,205)}
local names={'ReactorMode','ReactorTemperature','ReactorIntegrity'}
function StatusPanel.compute(mode,temp,integrity)
 mode=type(mode)=='string' and mode or ''
 local severity=severityByMode[mode] or 'standby'
 local temperature=type(temp)=='number' and temp==temp and math.abs(temp)<1e7 and string.format('%.0f °C',temp) or '— °C'
 local ratio=type(integrity)=='number' and integrity==integrity and math.clamp(integrity/100,0,1) or nil
 return {mode=mode,temperature=temperature,ratio=ratio,percent=ratio and string.format('%.1f%%',ratio*100) or '—',message=textByMode[mode] or 'VERİ BEKLENİYOR',severity=severity,color=colors[severity]}
end
local function label(parent,name,pos,size,text,sizePx)
 local x=Instance.new('TextLabel');x.Name=name;x.BackgroundTransparency=1;x.Position=pos;x.Size=size;x.Text=text;x.Font=Enum.Font.Code;x.TextSize=sizePx;x.TextColor3=Color3.fromRGB(224,235,228);x.TextScaled=true;x.Parent=parent;return x
end
-- screenFace is a BasePart placed on GLB display. lamps are explicitly mapped BaseParts,
-- not guessed by hierarchy names (Roblox importer may merge meshes/materials).
function StatusPanel.attach(screenFace, world, lamps, face)
 assert(screenFace and screenFace:IsA('BasePart'),'screenFace BasePart required')
 assert(world and world:IsA('Instance'),'reactor world required')
 assert(type(lamps)=='table' and #lamps==4,'four separately mapped lamp parts required')
 for _,lamp in ipairs(lamps) do assert(lamp:IsA('BasePart'),'lamp must be BasePart') end
 local prior=screenFace:FindFirstChild('AEGIS_DYNAMIC_STATUS');if prior then prior:Destroy() end
 local ui=Instance.new('SurfaceGui');ui.Name='AEGIS_DYNAMIC_STATUS';ui.Face=face or Enum.NormalId.Front;ui.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;ui.CanvasSize=Vector2.new(1600,490);ui.LightInfluence=0;ui.Parent=screenFace
 local bg=Instance.new('Frame');bg.Name='Background';bg.Size=UDim2.fromScale(1,1);bg.BackgroundColor3=Color3.fromRGB(10,17,18);bg.BorderSizePixel=0;bg.Parent=ui
 local temp=label(bg,'Temperature',UDim2.fromScale(.25,.05),UDim2.fromScale(.5,.14),'— °C',50)
 local mode=label(bg,'StateText',UDim2.fromScale(.10,.24),UDim2.fromScale(.8,.15),'VERİ BEKLENİYOR',48)
 local bar=Instance.new('Frame');bar.Name='BarBack';bar.Position=UDim2.fromScale(.12,.55);bar.Size=UDim2.fromScale(.76,.105);bar.BackgroundColor3=Color3.fromRGB(35,47,40);bar.BorderSizePixel=0;bar.Parent=bg
 local fill=Instance.new('Frame');fill.Name='BarFill';fill.Size=UDim2.fromScale(0,1);fill.BackgroundColor3=colors.normal;fill.BorderSizePixel=0;fill.Parent=bar
 local pct=label(bg,'Integrity',UDim2.fromScale(.18,.55),UDim2.fromScale(.64,.105),'REAKTÖR KALKANI —',32);pct.TextColor3=Color3.fromRGB(14,27,17)
 local diag=label(bg,'Diagnostics',UDim2.fromScale(.25,.78),UDim2.fromScale(.5,.10),'REAKTÖR TEŞHİSLERİ',28)
 local function update()
  local v=StatusPanel.compute(world:GetAttribute('ReactorMode'),world:GetAttribute('ReactorTemperature'),world:GetAttribute('ReactorIntegrity'))
  temp.Text=v.temperature;mode.Text=v.message;mode.TextColor3=v.color
  fill.Size=UDim2.fromScale(v.ratio or 0,1);fill.BackgroundColor3=v.color;pct.Text='REAKTÖR KALKANI  '..v.percent
  local selected= v.severity=='normal' and 1 or (v.severity=='warning' and 2 or (v.severity=='alarm' and 3 or 4))
  local lampColors={colors.normal,colors.warning,colors.alarm,colors.startup}
  for i,l in ipairs(lamps) do l.Color=lampColors[i];l.Material=i==selected and Enum.Material.Neon or Enum.Material.Metal;l.Transparency=i==selected and 0 or .4 end
 end
 local connections={};for _,n in ipairs(names) do connections[#connections+1]=world:GetAttributeChangedSignal(n):Connect(update) end;update()
 return {ui=ui,update=update,destroy=function() for _,c in ipairs(connections) do c:Disconnect() end;ui:Destroy() end}
end
return StatusPanel
