local rs=game:GetService('RunService');local w=workspace:FindFirstChild('CORE_PROTOCOL_V2_WORLD');local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local mov=a:FindFirstChild('MOVING');local tags={'UPPER','LEFT','RIGHT','LOWER_LEFT','LOWER_RIGHT','LOWER'}
local refs={};for _,tag in ipairs(tags) do local e=mov:FindFirstChild('REACTOR_EMITTER_REV03_'..tag);local p=e:FindFirstChild('NOZZLE__white',true);assert(p,'no nozzle '..tag);refs[tag]={e=e,p=p,pose=e:GetPivot():ToObjectSpace(p.CFrame)} end
local forced=0;local began=os.clock();local conn=rs.Heartbeat:Connect(function() w:SetAttribute('ReactorMode','MELTDOWN');w:SetAttribute('ReactorEmitterBrokenMask',forced);w:SetAttribute('ReactorEmitterReadyMask',63);w:SetAttribute('ReactorMeltdownAge',os.clock()-began) end)
local ok,res=xpcall(function()
 local report={}
 for i,tag in ipairs(tags) do forced=2^(i-1);task.wait(1)
  for j,other in ipairs(tags) do local item=refs[other];local status=item.e:GetAttribute('GLB_HeadCracked')==true;assert(status==(j==i),'bad failure state '..other..'/'..tag) end
  local r=refs[tag];local curr=r.e:GetPivot():ToObjectSpace(r.p.CFrame);local moved=(curr.Position-r.pose.Position).Magnitude
  local severity=r.e:GetAttribute('GLB_DamageSeverity');assert(severity and severity>.17,'severity '..tag);assert(moved>.01,'no deformation '..tag)
  local enabled=0;for _,d in ipairs(r.e:GetDescendants()) do if d:IsA('ParticleEmitter') and (d.Name=='BROKEN_NOZZLE_SMOKE' or d.Name=='METAL_ARC_AT_REAL_HEAD') and d.Enabled then enabled+=1 end end;assert(enabled==0,'2D particle emitted '..tag)
  local arcs=0;for _,d in ipairs(a:GetChildren()) do if d.Name=='EMITTER_DAMAGE_ARC_3D' and d:IsA('BasePart') then arcs+=1 end end
  report[#report+1]={tag=tag,bit=forced,severity=severity,movement=moved,arcs=arcs}
 end
 forced=0;task.wait(.8)
 for _,tag in ipairs(tags) do local r=refs[tag];local curr=r.e:GetPivot():ToObjectSpace(r.p.CFrame);local err=(curr.Position-r.pose.Position).Magnitude;assert(r.e:GetAttribute('GLB_HeadCracked')~=true and err<.01,'reset '..tag..' err '..err) end
 return game:GetService('HttpService'):JSONEncode(report)
end,debug.traceback)
conn:Disconnect();if not ok then error(res) end;return res
