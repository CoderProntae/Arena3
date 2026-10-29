local rs=game:GetService('RunService');local w=workspace:FindFirstChild('CORE_PROTOCOL_V2_WORLD');assert(w,'no world');local forced=0;local c=rs.Heartbeat:Connect(function() if forced then w:SetAttribute('ReactorPipeBrokenMask',forced) end end);local q={Invoke=function(_,v) if v=='RELEASE' then forced=nil;c:Disconnect() else forced=v end;return 'OK' end}
local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local static=a:FindFirstChild('STATIC');local kit=static:FindFirstChild('DAMAGE_PIPE_RUPTURE_KIT_01');local pipes=static:FindFirstChild('REACTOR_COOLANT_PIPING_RING_01');local fx=a:FindFirstChild('__FAZ42_VENT_3D');assert(kit and pipes and fx)
local names={'UPPER_LEFT','UPPER_RIGHT','REAR_LEFT','REAR_RIGHT'};local bits={5,2,7,0};local report={}
local function check(mask)
 assert(q:Invoke(mask)=='OK');task.wait(.4)
 local active,vents=0,0
 for i,n in ipairs(names) do
  local damaged=kit:FindFirstChild('PIPE_SPOOL_'..n..'_RUPTURED');local intact=pipes:FindFirstChild('PIPE_SPOOL_'..n)
  assert(damaged and intact,'missing '..n);local on=math.floor(mask/2^bits[i])%2==1
  assert(damaged:GetAttribute('Faz42Active')==on,'bad active '..n)
  for _,p in ipairs(damaged:GetDescendants()) do if p:IsA('MeshPart') then assert((p.Transparency<1)==on,'damage visibility '..n);active+=1 end end
  for _,p in ipairs(intact:GetDescendants()) do if p:IsA('MeshPart') then assert((p.Transparency==1)==on,'intact visibility '..n) end end
 end
 for _,p in ipairs(fx:GetChildren()) do if p:IsA('MeshPart') and p.Transparency<1 then vents+=1 end end
 local num=0;for _,i in ipairs(bits) do if math.floor(mask/2^i)%2==1 then num+=1 end end
 assert(vents==num*2,'vent count '..vents..' expected '..num*2)
 report[#report+1]={mask=mask,visibleVents=vents}
end
for _,m in ipairs({0,32,4,128,1,165,0}) do check(m) end
q:Invoke('RELEASE');return game:GetService('HttpService'):JSONEncode(report)
