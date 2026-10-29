local q=game:GetService('ServerStorage'):FindFirstChild('__M14_GLASS_QA');assert(q,'QA bindable missing')
local f=workspace:FindFirstChild('__M14_GLASS_LASER_VISUALS');assert(f,'controller missing')
local output={}
local function check(mode,age,level,hit,laserName)
 assert(q:Invoke(mode,age)=='QA_SET');task.wait(.12)
 local got=f:GetAttribute('Stage'); assert(got==level,string.format('stage at %s: expected %d got %s',tostring(age),level,tostring(got)))
 if hit then assert(f:GetAttribute('LastImpact')==hit,'wrong LastImpact '..tostring(f:GetAttribute('LastImpact'))) end
 if laserName then assert(f:FindFirstChild(laserName),'laser object missing at '..age) end
 output[#output+1]={age=age,stage=got,hit=f:GetAttribute('LastImpact'),final=f:GetAttribute('FinalImpact')}
end
check('COLD',0,0)
check('MELTDOWN',142,0)
check('MELTDOWN',143.1,1,143,'GlassImpactLaser')
check('MELTDOWN',229,1)
check('MELTDOWN',230.1,2,230,'GlassImpactLaser')
check('MELTDOWN',326,2)
check('MELTDOWN',327.1,3,327,'GlassImpactLaser')
check('MELTDOWN',384,3)
check('MELTDOWN',385.1,3,385,'GlassImpactLaser')
check('MELTDOWN',433,3)
check('MELTDOWN',434.1,3,434,'FinalGlassLaser')
assert(f:GetAttribute('FinalImpact')==true,'final flag missing')
check('AFTERMATH',0,0)
check('COLD',0,0)
assert(f:GetAttribute('LastImpact')==nil and f:GetAttribute('FinalImpact')==nil,'reset flags remain')
q:Invoke('RELEASE',0)
return game:GetService('HttpService'):JSONEncode(output)
