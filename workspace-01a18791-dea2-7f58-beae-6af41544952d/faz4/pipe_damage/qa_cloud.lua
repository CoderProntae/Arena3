local ss=game:GetService('ServerStorage');local q=ss:FindFirstChild('__FAZ42_PIPE_QA');assert(q,'no QA')
local a=workspace:FindFirstChild('REACTOR_MESH_ASSEMBLY');local st=a:FindFirstChild('STATIC');local kit=st:FindFirstChild('DAMAGE_PIPE_RUPTURE_KIT_01');local pipes=st:FindFirstChild('REACTOR_COOLANT_PIPING_RING_01');local fx=a:FindFirstChild('__FAZ42_VENT_3D');assert(kit and pipes and fx)
local names={'UPPER_LEFT','UPPER_RIGHT','REAR_LEFT','REAR_RIGHT'};local bits={5,2,7,0};local report={};local orig={}
q:Invoke(0);task.wait(.7)
for _,n in ipairs(names) do local intact=pipes:FindFirstChild('PIPE_SPOOL_'..n);for _,p in ipairs(intact:GetDescendants()) do if p:IsA('MeshPart') then orig[p]={p.Transparency,p.CanCollide,p.CanTouch,p.CanQuery} end end end
for _,mask in ipairs({0,32,4,128,1,165,0}) do
 q:Invoke(mask);task.wait(.65);local clouds=0;local num=0
 for i,n in ipairs(names) do
  local damaged=kit:FindFirstChild('PIPE_SPOOL_'..n..'_RUPTURED');local intact=pipes:FindFirstChild('PIPE_SPOOL_'..n);local on=math.floor(mask/2^bits[i])%2==1
  if on then num+=1 end
  assert(damaged:GetAttribute('Faz42Active')==on,'active '..n)
  for _,p in ipairs(damaged:GetDescendants()) do if p:IsA('MeshPart') then assert((p.Transparency<1)==on,'damaged '..n) end end
  for _,p in ipairs(intact:GetDescendants()) do if p:IsA('MeshPart') then
   local o=orig[p];assert(o,'missing saved state');assert(p.Transparency==(on and 1 or o[1]),'intact alpha '..n)
   assert(p.CanCollide==(not on and o[2]) and p.CanTouch==(not on and o[3]) and p.CanQuery==(not on and o[4]),'intact flags '..n)
  end end
 end
 for _,p in ipairs(fx:GetChildren()) do if p:IsA('MeshPart') and p.Transparency<1 then clouds+=1 end end
 assert(clouds==num*8,'cloud count '..clouds..' expected '..num*8)
 report[#report+1]={mask=mask,visibleClouds=clouds}
end
q:Invoke('RELEASE');return game:GetService('HttpService'):JSONEncode(report)
