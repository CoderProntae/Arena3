local rs=game:GetService('RunService');local w=workspace:FindFirstChild('CORE_PROTOCOL_V2_WORLD');local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local vent=a:FindFirstChild('__FAZ42_VENT_3D');local mov=a:FindFirstChild('MOVING');local saved={mode=w:GetAttribute('ReactorMode'),pipes=w:GetAttribute('ReactorPipeBrokenMask'),emit=w:GetAttribute('ReactorEmitterBrokenMask')}
local con=rs.Heartbeat:Connect(function() w:SetAttribute('ReactorMode','COLD');w:SetAttribute('ReactorPipeBrokenMask',0);w:SetAttribute('ReactorEmitterBrokenMask',0) end)
task.wait(1.5)
local heads={};for _,tag in ipairs({'UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'}) do local e=mov:FindFirstChild('REACTOR_EMITTER_REV03_'..tag);heads[tag]={broken=e:GetAttribute('GLB_HeadCracked'),severity=e:GetAttribute('GLB_DamageSeverity')} end
local n=0;for _,d in ipairs(vent:GetChildren()) do if d:IsA('MeshPart') and d.Transparency<1 then n+=1 end end
local pipeMask=vent:GetAttribute('PipeMask');con:Disconnect();w:SetAttribute('ReactorMode',saved.mode);w:SetAttribute('ReactorPipeBrokenMask',saved.pipes);w:SetAttribute('ReactorEmitterBrokenMask',saved.emit)
assert(n==0 and pipeMask==0,'visual pipe reset failed');for tag,h in pairs(heads) do assert(h.broken~=true and (not h.severity or h.severity==0),'head reset failed '..tag) end
return game:GetService('HttpService'):JSONEncode({ventCount=n,pipeMask=pipeMask,heads=heads})
