--[[
    HELIOS-9 V3 / CLIENT CINEMATICS
    StarterPlayer > StarterPlayerScripts > LocalScript

    Absolutely NO ScreenGui, HUD, countdown, warning text, mission panels,
    or interactive client controls. This script only plays the 3-minute
    soundtrack and applies local camera/color impulses caused by real
    server-side structural events. The server owns every lever and machine.
]]

local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local Lighting=game:GetService("Lighting")
local RunService=game:GetService("RunService")
local TweenService=game:GetService("TweenService")
local SoundService=game:GetService("SoundService")
local StarterGui=game:GetService("StarterGui")
local player=Players.LocalPlayer
-- Keep Roblox's chat/menu, but hide its default health/player-list/backpack
-- overlays too. The three world levers still work by click or touch.
task.spawn(function()
    for attempt=1,5 do
        local ok=pcall(function()
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Health,false)
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList,false)
            StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.Backpack,false)
        end)
        if ok then break end
        task.wait(0.7)
    end
end)
local remote=ReplicatedStorage:WaitForChild("HELIOS9_V3_CUES",30)
if not remote then
    warn("HELIOS-9 V3: Sunucu Script'i bulunamadı. V3 Server'i kurun.")
    return
end

local priorMusic=SoundService:FindFirstChild("HELIOS9_V3_ORIGINAL_SCORE")
if priorMusic then priorMusic:Destroy() end
local music=Instance.new("Sound")
music.Name="HELIOS9_V3_ORIGINAL_SCORE"
music.Volume=0
music.Looped=false
music.Parent=SoundService

local oldGrade=Lighting:FindFirstChild("HELIOS9_V3_LOCAL_FILM")
if oldGrade then oldGrade:Destroy() end
local grade=Instance.new("ColorCorrectionEffect")
grade.Name="HELIOS9_V3_LOCAL_FILM"
grade.Brightness=0
grade.Contrast=0
grade.Saturation=0
grade.TintColor=Color3.new(1,1,1)
grade.Parent=Lighting
local oldBlur=Lighting:FindFirstChild("HELIOS9_V3_LOCAL_BLUR")
if oldBlur then oldBlur:Destroy() end
local blur=Instance.new("BlurEffect")
blur.Name="HELIOS9_V3_LOCAL_BLUR"
blur.Size=0
blur.Parent=Lighting

local rng=Random.new()
local impulses={}
local elapsed=0
local musicVersion=0
local colorVersion=0
local activeMusicTween
local currentLoadedConnection
local currentSource=""

local function fadeMusic(volume,duration)
    if activeMusicTween then activeMusicTween:Cancel() end
    activeMusicTween=TweenService:Create(music,
        TweenInfo.new(duration,Enum.EasingStyle.Sine,
            Enum.EasingDirection.InOut),{Volume=volume})
    activeMusicTween:Play()
end
local function stopMusic()
    musicVersion=musicVersion+1
    local token=musicVersion
    fadeMusic(0,1.45)
    task.delay(1.52,function()
        if token==musicVersion then music:Stop() end
    end)
end
local function startMusic(id,position,serverStamp)
    if not id or id=="" then return end
    musicVersion=musicVersion+1
    local token=musicVersion
    if currentLoadedConnection then
        currentLoadedConnection:Disconnect()
        currentLoadedConnection=nil
    end
    if currentSource~=id then
        music:Stop()
        music.SoundId=id
        currentSource=id
    else
        music:Stop()
    end
    music.Volume=0
    music:Play()
    local from=math.max(0,tonumber(position) or 0)
    local function seek()
        if token~=musicVersion or not music.IsLoaded then return end
        local maxPosition=math.max(0,music.TimeLength-0.1)
        local lag=type(serverStamp)=="number" and
            math.max(0,workspace:GetServerTimeNow()-serverStamp) or 0
        if maxPosition>0 then
            music.TimePosition=math.min(from+lag,maxPosition)
        end
    end
    if music.IsLoaded then
        seek()
    else
        currentLoadedConnection=music.Loaded:Connect(function()
            seek()
            if currentLoadedConnection then
                currentLoadedConnection:Disconnect()
                currentLoadedConnection=nil
            end
        end)
    end
    fadeMusic(0.64,3.8)
end
local function flash(power,hue)
    colorVersion=colorVersion+1
    local token=colorVersion
    local strength=math.clamp(tonumber(power) or 0.2,0.05,1)
    local tint=hue=="red" and Color3.fromRGB(255,129,134)
        or hue=="orange" and Color3.fromRGB(255,194,128)
        or hue=="ice" and Color3.fromRGB(173,241,255)
        or Color3.fromRGB(255,255,255)
    grade.TintColor=tint
    grade.Brightness=math.min(0.72,strength*0.62)
    grade.Contrast=math.min(0.55,strength*0.30)
    blur.Size=math.min(23,strength*17)
    TweenService:Create(grade,
        TweenInfo.new(strength>0.9 and 3.3 or 0.84,
            Enum.EasingStyle.Quad,Enum.EasingDirection.Out),
        {Brightness=0,Contrast=0,TintColor=Color3.new(1,1,1)}):Play()
    TweenService:Create(blur,
        TweenInfo.new(strength>0.9 and 3.9 or 1.0),
        {Size=0}):Play()
    task.delay(4,function()
        if token==colorVersion then
            grade.Brightness=0
            blur.Size=0
        end
    end)
end

remote.OnClientEvent:Connect(function(kind,a,b,c,d)
    if kind=="MUSIC" then
        if a=="START" then
            startMusic(c,b,d)
        else
            stopMusic()
        end
    elseif kind=="TREMOR" then
        local amp=math.clamp(tonumber(a) or 0.3,0,4)
        local duration=math.clamp(tonumber(b) or 1,0.1,12)
        impulses[#impulses+1]={power=amp,left=duration,duration=duration,
            phase=rng:NextNumber(0,100)}
        while #impulses>8 do table.remove(impulses,1) end
    elseif kind=="FLASH" then
        flash(a,b)
    elseif kind=="RESET" then
        stopMusic()
        impulses={}
        grade.Brightness=0
        grade.Contrast=0
        grade.TintColor=Color3.new(1,1,1)
        blur.Size=0
    end
end)

RunService:BindToRenderStep("HELIOS9_V3_LOCAL_TREMORS",
    Enum.RenderPriority.Camera.Value+1,function(dt)
        elapsed=elapsed+dt
        local shake=0
        for i=#impulses,1,-1 do
            local entry=impulses[i]
            entry.left=entry.left-dt
            if entry.left<=0 then
                table.remove(impulses,i)
            else
                local decay=entry.left/entry.duration
                shake=shake+entry.power*decay*decay
            end
        end
        if shake<0.01 then return end
        local cam=workspace.CurrentCamera
        if not cam then return end
        local distance=(cam.CFrame.Position-Vector3.new(0,54,0)).Magnitude
        local falloff=math.clamp(1-distance/520,0.35,1)
        local value=math.min(1.35,shake)*falloff
        local x=math.noise(elapsed*21,0,0)*0.21*value
        local y=math.noise(0,elapsed*23,0)*0.24*value
        local z=math.noise(0,0,elapsed*15)*0.08*value
        local yaw=math.rad(math.noise(elapsed*15,4.3,0)*0.8*value)
        cam.CFrame=cam.CFrame*CFrame.new(x,y,z)*CFrame.Angles(0,yaw,0)
    end)

print("[HELIOS-9 V3] HUD yok; sinematik ses ve kamera hazır.")
