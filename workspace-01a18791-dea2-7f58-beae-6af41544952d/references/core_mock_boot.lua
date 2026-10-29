-- Temporary engineering test harness: approximates only a subset of Roblox.
local mtVec={}
local methodsVec={}
function methodsVec:Lerp(other,a) return Vector3.new(self.X+(other.X-self.X)*a,self.Y+(other.Y-self.Y)*a,self.Z+(other.Z-self.Z)*a) end
mtVec.__index=function(self,key)
 if key=='Magnitude' then return math.sqrt(self.X^2+self.Y^2+self.Z^2) end
 if key=='Unit' then local n=math.sqrt(self.X^2+self.Y^2+self.Z^2);return n>0 and Vector3.new(self.X/n,self.Y/n,self.Z/n) or Vector3.new(0,0,0) end
 return methodsVec[key]
end
mtVec.__add=function(a,b) return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z) end
mtVec.__sub=function(a,b) return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z) end
mtVec.__unm=function(a) return Vector3.new(-a.X,-a.Y,-a.Z) end
mtVec.__mul=function(a,b)
 if type(a)=='number' then return Vector3.new(a*b.X,a*b.Y,a*b.Z) end
 if type(b)=='number' then return Vector3.new(a.X*b,a.Y*b,a.Z*b) end
 error('Vector vector multiplication unexpected')
end
mtVec.__div=function(a,b) return Vector3.new(a.X/b,a.Y/b,a.Z/b) end
Vector3={new=function(x,y,z) return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},mtVec) end}
Vector3.zero=Vector3.new(0,0,0)
Vector2={new=function(x,y) return {X=x,Y=y} end}
local mtColor={}
function mtColor:Lerp(b,t) return Color3.new(self.R+(b.R-self.R)*t,self.G+(b.G-self.G)*t,self.B+(b.B-self.B)*t) end
mtColor.__index=mtColor
mtColor.__eq=function(a,b) return a.R==b.R and a.G==b.G and a.B==b.B end
Color3={new=function(r,g,b) return setmetatable({R=r,G=g,B=b},mtColor) end,fromRGB=function(r,g,b) return setmetatable({R=r/255,G=g/255,B=b/255},mtColor) end}
local mtCF={}
mtCF.__index=function(self,k) if k=='Position' then return self.p end end
mtCF.__mul=function(a,b)
 if getmetatable(b)==mtCF then return CFrame.new(a.p+b.p) end
 if getmetatable(b)==mtVec then return a.p+b end
 error('Unexpected CFrame product')
end
CFrame={new=function(x,y,z)
 if type(x)=='table' then return setmetatable({p=x},mtCF) end
 return setmetatable({p=Vector3.new(x or 0,y or 0,z or 0)},mtCF)
end,
 lookAt=function(a,b) return CFrame.new(a) end,
 Angles=function(...) return CFrame.new(0,0,0) end}
local function enumGroup(name) return setmetatable({}, {__index=function(_,k) if k=='Value' then return 200 end return name..'.'..k end}) end
Enum=setmetatable({RenderPriority=setmetatable({Camera={Value=200}}, {__index=function(_,k) return {Value=200} end})},{__index=function(_,key) local v=enumGroup(key);rawset(Enum,key,v);return v end})
NumberSequence={new=function(...)return {...} end}
NumberSequenceKeypoint={new=function(...)return {...} end}
ColorSequence={new=function(...)return {...} end}
NumberRange={new=function(...)return {...} end}
UDim2={fromScale=function(x,y)return {x,y} end}
TweenInfo={new=function(...)return {...} end}
RaycastParams={new=function()return {} end}
math.clamp=function(n,a,b) return math.max(a,math.min(b,n)) end
math.noise=function(x,y,z) return math.sin(x*1.1+y*2.4+z*0.7) end
local Seed={}
Seed.__index=Seed
function Seed:NextInteger(a,b) return math.random(a,b) end
function Seed:NextNumber(a,b) return a+(b-a)*math.random() end
Random={new=function(n) math.randomseed(n);return setmetatable({},Seed) end}

local current=0
local queue={}
local coCurrent=nil
local function schedule(fn,delay)
 queue[#queue+1]={at=current+(delay or 0),fn=fn}
end
time=function()return current end
function __mock_time() return current end
function __mock_advance(dt)
 current=current+dt
 local i=1
 while i<=#queue do
  local job=queue[i]
  if current>=job.at then table.remove(queue,i);job.fn() else i=i+1 end
 end
end
task={delay=function(dt,fn) schedule(fn,dt) end,
 spawn=function(fn,...)
  local args={...}
  local co=coroutine.create(function() fn(table.unpack(args)) end)
  local function run()
   local ok,waitTime=coroutine.resume(co)
   if not ok then error(waitTime) end
   if coroutine.status(co)~='dead' then schedule(run,waitTime or 0.01) end
  end
  schedule(run,0)
 end,
 wait=function(dt) return coroutine.yield(dt or 0.05) end}
local function signal()
 local s={listeners={}}
 function s:Connect(fn) self.listeners[#self.listeners+1]=fn;return {Disconnect=function()end} end
 function s:Fire(...) for _,fn in ipairs(self.listeners) do fn(...) end end
 return s
end
local instanceFunctions={}
function instanceFunctions:GetChildren() return self._children end
function instanceFunctions:GetDescendants()
 local all={}
 local function descend(p)for _,c in ipairs(p._children)do all[#all+1]=c;descend(c)end end
 descend(self);return all
end
function instanceFunctions:FindFirstChild(name)
 for _,c in ipairs(self._children)do if c.Name==name then return c end end
end
function instanceFunctions:FindFirstChildOfClass(class)
 for _,c in ipairs(self._children)do if c.ClassName==class then return c end end
end
function instanceFunctions:WaitForChild(name,timeout) return self:FindFirstChild(name) end
function instanceFunctions:IsA(class) return self.ClassName==class or class=='Instance' or (class=='BasePart' and (self.ClassName=='Part' or self.ClassName=='SpawnLocation')) end
function instanceFunctions:IsDescendantOf(parent)
 local p=self.Parent
 while p do if p==parent then return true end p=p.Parent end
 return false
end
function instanceFunctions:Destroy()
 if self.Parent then local children=self.Parent._children;for i=#children,1,-1 do if children[i]==self then table.remove(children,i)break end end end
 self._values.Parent=nil
 for _,c in ipairs(self._children)do c._values.Parent=nil end
 self._children={}
end
function instanceFunctions:ClearAllChildren()
 for _,c in ipairs(self._children)do c._values.Parent=nil end
 self._children={}
end
function instanceFunctions:SetAttribute(key,val) self._attributes[key]=val end
function instanceFunctions:GetAttribute(key) return self._attributes[key] end
function instanceFunctions:Play()self.IsPlaying=true end
function instanceFunctions:Stop()self.IsPlaying=false end
function instanceFunctions:Emit(n) self.Emitted=(self.Emitted or 0)+n end
function instanceFunctions:FireAllClients(...) __mock_sent[#__mock_sent+1]={at=current,args={...}} end
function instanceFunctions:FireClient(player,...) __mock_sent[#__mock_sent+1]={at=current,args={...}} end
function instanceFunctions:FireServer(...)self.OnServerEvent:Fire(__mock_player,...)end
function instanceFunctions:TakeDamage(n) self.Health=math.max(0,self.Health-n) end
local instanceMeta={}
instanceMeta.__index=function(self,key)
 if instanceFunctions[key] then return instanceFunctions[key] end
 if key=='Position' then local f=self._values.CFrame;return f and f.Position or self._values.Position end
 return self._values[key]
end
instanceMeta.__newindex=function(self,key,val)
 if key=='Parent' then
  local prev=self._values.Parent
  if prev and prev._children then for i=#prev._children,1,-1 do if prev._children[i]==self then table.remove(prev._children,i)break end end end
  self._values.Parent=val
  if val and val._children then val._children[#val._children+1]=self end
 elseif key=='Position' then
  self._values.CFrame=CFrame.new(val)
 else self._values[key]=val end
end
Instance={new=function(kind)
 local v={Name=kind,ClassName=kind,Transparency=0,
 Material='Material.Metal',Color=Color3.new(1,1,1),
 Size=Vector3.new(1,1,1),CanCollide=false,CanQuery=true,
 CFrame=CFrame.new(0,0,0),Health=100,
 IsPlaying=false,IsLoaded=true,TimeLength=180,FieldOfView=70}
 local obj=setmetatable({_children={},_values=v,_attributes={}},instanceMeta)
 if kind=='ClickDetector' then obj.MouseClick=signal() end
 if kind=='RemoteEvent' then obj.OnServerEvent=signal();obj.OnClientEvent=signal() end
 if kind=='Sound' then obj.Loaded=signal() end
 return obj
end}
__mock_sent={}
local services={}
for _,name in ipairs({'Workspace','ReplicatedStorage','Lighting','Players','RunService','TweenService','Debris','SoundService'})do
 services[name]=Instance.new(name)
end
local players=services.Players
players.PlayerAdded=signal();players.PlayerRemoving=signal();players.LocalPlayer=nil
function players:GetPlayers() return self._players or {} end
local run=services.RunService
run.Heartbeat=signal()
function run:IsStudio() return false end
function run:BindToRenderStep(name,priority,callback) self._render=callback end
function run:UnbindFromRenderStep(name)self._render=nil end
local tween=services.TweenService
function tween:Create(obj,info,props)
 return {Play=function()
  for k,v in pairs(props)do obj[k]=v end
 end,Cancel=function()end}
end
local debris=services.Debris
function debris:AddItem(obj,secs) schedule(function()if obj.Parent then obj:Destroy()end end,secs)end
local workspace=services.Workspace
function workspace:Raycast(a,b,params)return nil end
function workspace:GetServerTimeNow()return 1700000000+current end
workspace.CurrentCamera=Instance.new('Camera')
local player=Instance.new('Player')
player.Name='Tester';player.UserId=419
player.CharacterAdded=signal()
local character=Instance.new('Model');character.Name='Character';character.Parent=player
local root=Instance.new('Part');root.Name='HumanoidRootPart';root.CFrame=CFrame.new(0,28,149);root.Parent=character
local human=Instance.new('Humanoid');human.Name='Humanoid';human.Health=100;human.Parent=character
player.Character=character
local gui=Instance.new('PlayerGui');gui.Name='PlayerGui';gui.Parent=player
players._players={player};players.LocalPlayer=player
__mock_player=player
__mock_services=services
__mock_root=root
__mock_character=character
__mock_humanoid=human
__mock_find=function(name)
 for _,service in pairs(services) do
  if service.Name==name then return service end
  for _,c in ipairs(service:GetDescendants()) do if c.Name==name then return c end end
 end
end
function __mock_click_control(station)
 local group=__mock_find(station..'_FUNCTIONAL_STATION')
 if not group then error('Station missing '..station) end
 local detector=nil
 for _,item in ipairs(group:GetDescendants()) do
  if item.ClassName=='ClickDetector' then detector=item;break end
 end
 if not detector then error('Detector missing '..station) end
 __mock_root.CFrame=CFrame.new(detector.Parent.Position+Vector3.new(0,0,7))
 detector.MouseClick:Fire(player)
end
function __mock_collect_cards()
 local found=0
 local cards={}
 for _,c in ipairs(__mock_services.Workspace:GetDescendants()) do
  if c.Name=='PICKUP_REACTOR_AUTH_CARD' and c.CanQuery then
   cards[#cards+1]=c
  end
 end
 for _,c in ipairs(cards) do
  __mock_root.CFrame=CFrame.new(c.Position+Vector3.new(0,2,5))
  c:FindFirstChildOfClass('ClickDetector').MouseClick:Fire(__mock_player)
  found=found+1
 end
 return found
end
function __mock_click(part)
 local target=__mock_find(part)
 if not target then error('Clickable object missing '..part) end
 local detector=target:FindFirstChildOfClass('ClickDetector')
 if not detector then error('ClickDetector missing '..part) end
 __mock_root.CFrame=CFrame.new(target.Position+Vector3.new(0,3,6))
 detector.MouseClick:Fire(player)
end
function __mock_step(dt)
 __mock_advance(dt)
 __mock_services.RunService.Heartbeat:Fire(dt)
end
function __mock_state()
 local label=__mock_find('OVER_WINDOW_EMERGENCY_LETTERBOX')
 return label and label:FindFirstChild('ENGRAVED_VIEW')
end
game={GetService=function(_,name) return services[name] end}
print=function(...)end
warn=function(...)io.stderr:write('[LUA MOCK WARNING] '..table.concat({...},' ')..'\n')end
