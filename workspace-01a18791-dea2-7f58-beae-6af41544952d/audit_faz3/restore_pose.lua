local WS=game:GetService("Workspace")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local moving=assembly:WaitForChild("MOVING")
local n=assembly:GetAttribute("AUDHOME_N") or 0
local done=0
for i=1,n do
 local s=assembly:GetAttribute("AUDHOME_"..i)
 if s then
  local path, nums = s:match("^(.-)|(.+)$")
  local cur=moving
  for seg in path:gmatch("[^/]+") do cur=cur and cur:FindFirstChild(seg) end
  if cur then
   local t={}
   for v in nums:gmatch("[^,]+") do t[#t+1]=tonumber(v) end
   cur:PivotTo(CFrame.new(table.unpack(t)))
   done+=1
  end
  assembly:SetAttribute("AUDHOME_"..i, nil)
 end
end
assembly:SetAttribute("AUDHOME_N", nil)
for _,tag in ipairs({"UPPER","LOWER","LOWER_LEFT","LOWER_RIGHT"}) do assembly:SetAttribute("LiveGate_"..tag, 0) end
return "geri alindi="..done.."/"..n
