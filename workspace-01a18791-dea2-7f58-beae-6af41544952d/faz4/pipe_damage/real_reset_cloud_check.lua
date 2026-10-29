local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',10);local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',10);local st=a:WaitForChild('STATIC',10);local kit=st:WaitForChild('DAMAGE_PIPE_RUPTURE_KIT_01',10);local pipes=st:WaitForChild('REACTOR_COOLANT_PIPING_RING_01',10);local vent=a:WaitForChild('__FAZ42_VENT_3D',10)
local deadline=os.clock()+75;while w:GetAttribute('ReactorMode')~='COLD' and os.clock()<deadline do task.wait(.5) end
assert(w:GetAttribute('ReactorMode')=='COLD','no reset');task.wait(.6)
local mask=w:GetAttribute('ReactorPipeBrokenMask');local n=0;for _,p in ipairs(vent:GetChildren()) do if p:IsA('MeshPart') and p.Transparency<1 then n+=1 end end
assert(mask==0 and vent:GetAttribute('PipeMask')==0 and n==0,'mask/vent not reset')
local spools={};for _,name in ipairs({'UPPER_LEFT','UPPER_RIGHT','REAR_LEFT','REAR_RIGHT'}) do
 local d=kit:FindFirstChild('PIPE_SPOOL_'..name..'_RUPTURED');local orig=pipes:FindFirstChild('PIPE_SPOOL_'..name)
 assert(d:GetAttribute('Faz42Active')==false,'damage flag '..name)
 local vis=0;for _,p in ipairs(orig:GetDescendants()) do if p:IsA('MeshPart') and p.Transparency<1 then vis+=1 end end
 local dvis=0;for _,p in ipairs(d:GetDescendants()) do if p:IsA('MeshPart') and p.Transparency<1 then dvis+=1 end end
 assert(vis==6 and dvis==0,'model restore '..name);spools[name]={intact=vis,damaged=dvis}
end
return game:GetService('HttpService'):JSONEncode({mode=w:GetAttribute('ReactorMode'),mask=mask,clouds=n,spools=spools})
