local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30)
local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',30)
local root=a:WaitForChild('REAL_3D_VOLUMETRIC_MODELS',60)
local name='__FAZ43_CLIENT_QA';local prev=workspace:FindFirstChild(name);if prev then prev:Destroy() end
local out=Instance.new('Folder');out.Name=name;out.Parent=workspace
local http=game:GetService('HttpService')
local tags={'UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'}
local function sample()
 local rays={};for _,tag in ipairs(tags) do local p=root:FindFirstChild('LASER_3D_CORE_'..tag,true);rays[tag]=p and p.Transparency or -1 end
 return {mask=w:GetAttribute('ReactorEmitterBrokenMask'),count=workspace:GetAttribute('LaserActiveCount'),rays=rays}
end
task.spawn(function()
 local times={143,186,230,271,345};local seen={};local began=false;local t0=os.clock()
 while out.Parent and os.clock()-t0<540 do
  local mode=w:GetAttribute('ReactorMode');local age=w:GetAttribute('ReactorMeltdownAge') or 0
  if mode=='MELTDOWN' then began=true;for _,at in ipairs(times) do if age>=at+1 and not seen[at] then seen[at]=true;local d=sample();d.age=age;out:SetAttribute('T'..at,http:JSONEncode(d)) end end
  elseif began and mode=='AFTERMATH' and not seen.aftermath then seen.aftermath=true;task.wait(1);out:SetAttribute('AFTERMATH',http:JSONEncode(sample()))
  elseif began and mode=='COLD' then task.wait(1);out:SetAttribute('RESET',http:JSONEncode(sample()));out:SetAttribute('Done',true);return end
  task.wait(.15)
 end
 out:SetAttribute('Timeout',true)
end)
return 'CLIENT_MONITOR_READY'
