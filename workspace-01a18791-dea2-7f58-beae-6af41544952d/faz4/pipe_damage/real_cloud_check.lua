local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30);local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',30);local s=a:WaitForChild('STATIC',30);local kit=s:WaitForChild('DAMAGE_PIPE_RUPTURE_KIT_01',30);local pipes=s:WaitForChild('REACTOR_COOLANT_PIPING_RING_01',30);local vent=a:WaitForChild('__FAZ42_VENT_3D',30)
local deadline=os.clock()+35
while w:GetAttribute('ReactorMode')~='MELTDOWN' and w:GetAttribute('ReactorMode')~='AFTERMATH' and os.clock()<deadline do task.wait(.3) end
task.wait(2)
local mask=w:GetAttribute('ReactorPipeBrokenMask');local visual=vent:GetAttribute('PipeMask');local active={};local visible=0
local names={'UPPER_LEFT','UPPER_RIGHT','REAR_LEFT','REAR_RIGHT'};local bits={5,2,7,0}
for i,n in ipairs(names) do
 local d=kit:FindFirstChild('PIPE_SPOOL_'..n..'_RUPTURED');local intact=pipes:FindFirstChild('PIPE_SPOOL_'..n);local on=math.floor(mask/2^bits[i])%2==1
 active[n]=d:GetAttribute('Faz42Active');assert(on and active[n],'expected broken '..n)
 for _,p in ipairs(intact:GetDescendants()) do if p:IsA('MeshPart') then assert(p.Transparency==1 and not p.CanCollide and not p.CanTouch and not p.CanQuery,'intact '..n) end end
end
for _,p in ipairs(vent:GetChildren()) do if p:IsA('MeshPart') and p.Transparency<1 then visible+=1 end end
assert(visual==mask,'mask mismatch');assert(visible==32,'clouds '..visible)
return game:GetService('HttpService'):JSONEncode({mode=w:GetAttribute('ReactorMode'),age=w:GetAttribute('ReactorMeltdownAge'),pipeMask=mask,visualMask=visual,visibleClouds=visible,spools=active})
