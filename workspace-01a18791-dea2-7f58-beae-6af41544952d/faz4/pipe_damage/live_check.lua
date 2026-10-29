local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30);local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',30);local s=a:WaitForChild('STATIC',10);local kit=s:WaitForChild('DAMAGE_PIPE_RUPTURE_KIT_01',20);local vent=a:WaitForChild('__FAZ42_VENT_3D',20)
local untilTime=os.clock()+40
while w:GetAttribute('ReactorMode')~='MELTDOWN' and os.clock()<untilTime do task.wait(.5) end
assert(w:GetAttribute('ReactorMode')=='MELTDOWN','no meltdown')
task.wait(2)
local mask=w:GetAttribute('ReactorPipeBrokenMask');local visual=vent:GetAttribute('PipeMask');local broken=w:GetAttribute('ReactorEmitterBrokenMask');local active={};local nvent=0
for _,d in ipairs(kit:GetChildren()) do active[d.Name]=d:GetAttribute('Faz42Active') end
for _,d in ipairs(vent:GetChildren()) do if d:IsA('MeshPart') and d.Transparency<1 then nvent+=1 end end
local heads={};local mov=a:FindFirstChild('MOVING')
for _,tag in ipairs({'UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'}) do local e=mov:FindFirstChild('REACTOR_EMITTER_REV03_'..tag);heads[tag]={broken=e:GetAttribute('GLB_HeadCracked'),severity=e:GetAttribute('GLB_DamageSeverity')} end
assert(mask==visual,'mask mismatch '..tostring(mask)..'/'..tostring(visual));assert(mask==164,'unexpected mask '..tostring(mask));assert(nvent==6,'unexpected vent count '..nvent)
assert(active.PIPE_SPOOL_UPPER_LEFT_RUPTURED==true and active.PIPE_SPOOL_UPPER_RIGHT_RUPTURED==true and active.PIPE_SPOOL_REAR_LEFT_RUPTURED==true and active.PIPE_SPOOL_REAR_RIGHT_RUPTURED==false,'unexpected spools')
return game:GetService('HttpService'):JSONEncode({mode=w:GetAttribute('ReactorMode'),age=w:GetAttribute('ReactorMeltdownAge'),pipeMask=mask,visualMask=visual,brokenEmitters=broken,ventCount=nvent,spools=active,heads=heads})
