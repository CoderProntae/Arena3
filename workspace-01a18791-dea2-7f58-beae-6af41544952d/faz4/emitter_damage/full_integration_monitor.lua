local w=workspace:WaitForChild('CORE_PROTOCOL_V2_WORLD',30)
local a=workspace:WaitForChild('REACTOR_MESH_ASSEMBLY',30)
local mov=a:WaitForChild('MOVING',10)
local vents=a:WaitForChild('__FAZ42_VENT_3D',30)
local glass=workspace:WaitForChild('__M14_GLASS_LASER_VISUALS',30)
local tags={'UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'}
local refs={};for i,tag in ipairs(tags) do local e=mov:FindFirstChild('REACTOR_EMITTER_REV03_'..tag);local p=e:FindFirstChild('NOZZLE__white',true);refs[i]={tag=tag,e=e,p=p,base=e:GetPivot():ToObjectSpace(p.CFrame)} end
local out=workspace:FindFirstChild('__FAZ43_FULL_QA');if out then out:Destroy() end;out=Instance.new('Folder');out.Name='__FAZ43_FULL_QA';out.Parent=workspace
local http=game:GetService('HttpService')
local function sample()
 local heads={};local bad2d=0
 for _,r in ipairs(refs) do
  local relative=r.e:GetPivot():ToObjectSpace(r.p.CFrame)
  heads[r.tag]={broken=r.e:GetAttribute('GLB_HeadCracked')==true,severity=r.e:GetAttribute('GLB_DamageSeverity') or 0,delta=(relative.Position-r.base.Position).Magnitude}
  for _,p in ipairs(r.e:GetDescendants()) do if p:IsA('ParticleEmitter') and (p.Name=='BROKEN_NOZZLE_SMOKE' or p.Name=='METAL_ARC_AT_REAL_HEAD') and p.Enabled then bad2d+=1 end end
 end
 local cloud,arcs=0,0
 for _,p in ipairs(vents:GetChildren()) do if p:IsA('MeshPart') and p.Transparency<1 then cloud+=1 end end
 for _,p in ipairs(a:GetChildren()) do if p.Name=='EMITTER_DAMAGE_ARC_3D' and p:IsA('BasePart') then arcs+=1 end end
 return {brokenMask=w:GetAttribute('ReactorEmitterBrokenMask'),pipeMask=w:GetAttribute('ReactorPipeBrokenMask'),ventMask=vents:GetAttribute('PipeMask'),clouds=cloud,glassStage=glass:GetAttribute('Stage'),glassFinal=glass:GetAttribute('FinalImpact'),shards=w:GetAttribute('M14GlassShardTriangles'),legacy2D=bad2d,arcs3D=arcs,heads=heads}
end
task.spawn(function()
 local checkpoints={143,186,230,271,345,434};local seen={};local began=false;local t0=os.clock()
 while out.Parent and os.clock()-t0<540 do
  local mode=w:GetAttribute('ReactorMode');local age=w:GetAttribute('ReactorMeltdownAge') or 0
  if mode=='MELTDOWN' then began=true;for _,at in ipairs(checkpoints) do if age>=at+.48 and not seen[at] then seen[at]=true;local q=sample();q.age=age;out:SetAttribute('T'..at,http:JSONEncode(q)) end end
  elseif began and mode=='AFTERMATH' and not seen.aftermath then seen.aftermath=true;task.wait(.3);out:SetAttribute('AFTERMATH',http:JSONEncode(sample()))
  elseif began and mode=='COLD' then task.wait(.8);out:SetAttribute('RESET',http:JSONEncode(sample()));out:SetAttribute('Done',true);return end
  task.wait(.1)
 end
 out:SetAttribute('Timeout',true)
end)
return 'SERVER_MONITOR_READY'
