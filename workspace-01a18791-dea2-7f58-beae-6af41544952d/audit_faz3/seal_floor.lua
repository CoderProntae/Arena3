assert(game.Name=="AEGIS_Reactor.rbxlx")
local RS=game:GetService("RunService"); assert(RS:IsEdit(), "Edit degil")
local WS=game:GetService("Workspace")
local H=game:GetService("HttpService")
local assembly=WS:WaitForChild("REACTOR_MESH_ASSEMBLY")
local staticRoot=assembly:WaitForChild("STATIC")
local old=staticRoot:FindFirstChild("DENETIM_MUHUR_ZEMIN_01")
if old then old:Destroy() end
local deckColor=Color3.fromRGB(38,44,54)
local crown=staticRoot:FindFirstChild("REACTOR_CROWN_AND_DECK_01")
if crown then
 local gm=crown:FindFirstChild("CROWN_DECK__gunmetal", true)
 if gm and gm:IsA("BasePart") then deckColor=gm.Color end
end
local seal=Instance.new("Part")
seal.Name="DENETIM_MUHUR_ZEMIN_01"
seal.Size=Vector3.new(1.8, 0.3, 4.6)
seal.CFrame=CFrame.new(0, 5.88, 13.0)
seal.Anchored=true
seal.CanCollide=false
seal.CanQuery=true
seal.CanTouch=false
seal.Material=Enum.Material.Metal
seal.Color=deckColor
seal.TopSurface=Enum.SurfaceType.Smooth
seal.BottomSurface=Enum.SurfaceType.Smooth
seal:SetAttribute("AuditFix", "Faz4-oncesi denetim 28Ekim2026: CROWN_DECK merkez yarigi x=0 z12-14 muhur")
seal.Parent=staticRoot
-- dogrulama: x=0 hatti dikey isinlar
local res={}
for _,gz in ipairs({11.5,12,12.5,13,13.5,14,14.5}) do
 local hit=WS:Raycast(Vector3.new(0,30,gz), Vector3.new(0,-40,0))
 res[#res+1]=string.format("z=%.1f -> %s", gz, hit and (hit.Instance.Name.." @y="..string.format("%.2f",hit.Position.Y)) or "ESCAPE!")
end
return H:JSONEncode({seal="yerlestirildi", color=tostring(deckColor), rays=res})
